import asyncio
import imaplib
import logging
import select
import time
from typing import Any

from src.core.config import ImapProviderSettings
from src.modules.email.application.dto.email_message_dto import EmailMessageDTO
from src.modules.email.application.ports.imap_client import ImapClientPort
from src.modules.email.infrastructure.imap.parsers.mime_parser import MimeParser

logger = logging.getLogger(__name__)


class ImapIdleClient(ImapClientPort):
    def __init__(
        self,
        provider: str,
        settings: ImapProviderSettings,
        parser: MimeParser | None = None,
        mailbox: str = "INBOX",
        idle_timeout_sec: int = 60,
    ) -> None:
        self._provider = provider
        self._settings = settings
        self._parser = parser or MimeParser()
        self._mailbox = mailbox
        self._idle_timeout_sec = idle_timeout_sec
        self._client: imaplib.IMAP4 | imaplib.IMAP4_SSL | None = None

    async def connect(self) -> None:
        await asyncio.to_thread(self._connect_sync)

    async def idle_wait(self) -> None:
        await asyncio.to_thread(self._idle_wait_sync)

    async def fetch_new_messages(self, *, since_uid: int) -> list[EmailMessageDTO]:
        return await asyncio.to_thread(self._fetch_new_messages_sync, since_uid)

    async def get_latest_uid(self) -> int:
        return await asyncio.to_thread(self._get_latest_uid_sync)

    async def disconnect(self) -> None:
        await asyncio.to_thread(self._disconnect_sync)

    def _connect_sync(self) -> None:
        if self._client is not None:
            logger.debug("IMAP already connected: provider=%s", self._provider)
            return

        logger.info(
            "Connecting IMAP: provider=%s server=%s:%s ssl=%s mailbox=%s",
            self._provider,
            self._settings.server,
            self._settings.port,
            self._settings.use_ssl,
            self._mailbox,
        )
        client_cls: Any = imaplib.IMAP4_SSL if self._settings.use_ssl else imaplib.IMAP4
        client = client_cls(self._settings.server, self._settings.port)
        client.login(self._settings.username, self._settings.password)
        status, _ = client.select(self._mailbox)
        if status != "OK":
            raise RuntimeError(f"Cannot select mailbox {self._mailbox}")
        self._client = client
        logger.info("IMAP connected: provider=%s user=%s", self._provider, self._settings.username)

    def _idle_wait_sync(self) -> None:
        if self._client is None:
            raise RuntimeError("IMAP client is not connected")

        logger.info("IMAP IDLE start: provider=%s timeout=%ss", self._provider, self._idle_timeout_sec)
        tag = self._client._new_tag()
        self._client.send(f"{tag} IDLE\r\n".encode())
        line = self._client._get_line()
        if not line.startswith(b"+"):
            raise RuntimeError(f"IDLE was not accepted: {line!r}")

        sock = self._client.sock
        if sock is None:
            raise RuntimeError("No IMAP socket available for IDLE")

        ready, _, _ = select.select([sock], [], [], self._idle_timeout_sec)
        if ready:
            logger.info("IMAP IDLE event received: provider=%s", self._provider)
            try:
                _ = self._client._get_line()
            except Exception:
                logger.exception("Failed while reading IMAP IDLE response")
        else:
            logger.info("IMAP IDLE timeout: provider=%s", self._provider)

        self._client.send(b"DONE\r\n")
        self._finish_idle(tag)

    def _fetch_new_messages_sync(self, since_uid: int) -> list[EmailMessageDTO]:
        if self._client is None:
            raise RuntimeError("IMAP client is not connected")

        start_uid = max(1, since_uid + 1)
        logger.info(
            "Searching IMAP messages: provider=%s uid_range=%s:*",
            self._provider,
            start_uid,
        )
        # Use UID SEARCH with explicit range; avoid passing None as a literal token.
        status, data = self._client.uid("SEARCH", "UID", f"{start_uid}:*")
        if status != "OK":
            logger.warning(
                "IMAP SEARCH failed: provider=%s status=%s data=%r",
                self._provider,
                status,
                data,
            )
            return []
        if not data or not data[0]:
            logger.info("No new IMAP messages: provider=%s since_uid=%s", self._provider, since_uid)
            return []

        logger.info("IMAP SEARCH raw uid list: provider=%s data=%r", self._provider, data[0])
        result: list[EmailMessageDTO] = []
        for raw_uid in data[0].split():
            uid = int(raw_uid.decode())
            if uid <= since_uid:
                logger.warning(
                    "Skip stale UID from server: provider=%s uid=%s since_uid=%s",
                    self._provider,
                    uid,
                    since_uid,
                )
                continue
            fetch_status, fetch_data = self._client.uid("FETCH", raw_uid, "(RFC822)")
            if fetch_status != "OK" or not fetch_data:
                continue

            raw_email = self._extract_raw_email(fetch_data)
            if raw_email is None:
                continue

            result.append(self._parser.to_dto(provider=self._provider, uid=uid, raw_email=raw_email))

        logger.info("Fetched IMAP messages: provider=%s count=%s", self._provider, len(result))
        return result

    def _get_latest_uid_sync(self) -> int:
        if self._client is None:
            raise RuntimeError("IMAP client is not connected")
        status, data = self._client.uid("SEARCH", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return 0
        uids = data[0].split()
        if not uids:
            return 0
        return int(uids[-1].decode())

    def _disconnect_sync(self) -> None:
        if self._client is None:
            return
        logger.info("Disconnecting IMAP: provider=%s", self._provider)
        try:
            self._client.close()
        except Exception:
            pass
        try:
            self._client.logout()
        finally:
            self._client = None
            logger.info("IMAP disconnected: provider=%s", self._provider)

    def _finish_idle(self, tag: bytes, timeout_sec: float = 5.0) -> None:
        """Finish IDLE without risking an infinite block on _get_line()."""
        if self._client is None:
            return
        sock = self._client.sock
        if sock is None:
            return

        end_time = time.monotonic() + timeout_sec
        while True:
            remaining = max(0.0, end_time - time.monotonic())
            if remaining <= 0:
                logger.warning(
                    "IMAP DONE response timeout: provider=%s, continuing loop",
                    self._provider,
                )
                return

            ready, _, _ = select.select([sock], [], [], remaining)
            if not ready:
                logger.warning(
                    "IMAP DONE response not received in time: provider=%s",
                    self._provider,
                )
                return

            response_line = self._client._get_line()
            if response_line.startswith(tag):
                return

    @staticmethod
    def _extract_raw_email(fetch_data: list[Any]) -> bytes | None:
        for item in fetch_data:
            if isinstance(item, tuple) and len(item) > 1 and isinstance(item[1], (bytes, bytearray)):
                return bytes(item[1])
        return None