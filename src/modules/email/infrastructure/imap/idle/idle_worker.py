import asyncio
import logging

from src.modules.email.application.ports.imap_client import ImapClientPort
from src.modules.email.application.services.email_processing_service import EmailProcessingService
from src.modules.email.infrastructure.imap.idle.reconnect import ReconnectBackoff

logger = logging.getLogger(__name__)


class ImapIdleWorker:
    def __init__(
        self,
        account_key: str,
        client: ImapClientPort,
        processing_service: EmailProcessingService,
        backoff: ReconnectBackoff | None = None,
    ) -> None:
        self._account_key = account_key
        self._client = client
        self._processing_service = processing_service
        self._backoff = backoff or ReconnectBackoff()
        self._running = False

    async def run(self) -> None:
        self._running = True
        logger.info("IMAP worker started: account=%s", self._account_key)
        while self._running:
            try:
                logger.info("IMAP worker connecting: account=%s", self._account_key)
                await self._client.connect()
                self._backoff.reset()
                logger.info("IMAP worker connected: account=%s", self._account_key)
                # Initial sync right after connect catches missed messages
                # that arrived while worker was offline.
                initial_processed = await self._processing_service.poll_once()
                logger.info(
                    "IMAP initial poll completed: account=%s count=%s",
                    self._account_key,
                    initial_processed,
                )

                while self._running:
                    logger.info("IMAP worker entering IDLE: account=%s", self._account_key)
                    await self._client.idle_wait()
                    logger.info("IMAP worker left IDLE, polling mailbox: account=%s", self._account_key)
                    processed = await self._processing_service.poll_once()
                    if processed:
                        logger.info(
                            "IMAP worker processed messages: account=%s count=%s",
                            self._account_key,
                            processed,
                        )
            except asyncio.CancelledError:
                logger.info("IMAP worker cancelled: account=%s", self._account_key)
                raise
            except Exception:
                delay = self._backoff.next_delay()
                logger.exception(
                    "IMAP worker failure: account=%s reconnect_in=%.1fs",
                    self._account_key,
                    delay,
                )
                await asyncio.sleep(delay)
            finally:
                await self._client.disconnect()
        logger.info("IMAP worker stopped: account=%s", self._account_key)

    def stop(self) -> None:
        logger.info("Stop signal for IMAP worker: account=%s", self._account_key)
        self._running = False