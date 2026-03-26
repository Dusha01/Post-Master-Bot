import logging

from src.modules.email.application.ports.imap_client import ImapClientPort
from src.modules.email.application.ports.notifier import NotifierPort
from src.modules.email.application.ports.state_store import StateStorePort
from src.modules.email.domain.policies.email_delivery_policy import EmailDeliveryPolicy

logger = logging.getLogger(__name__)


class EmailProcessingService:
    def __init__(
        self,
        imap_client: ImapClientPort,
        notifier: NotifierPort,
        state_store: StateStorePort,
        account_key: str,
        policy: EmailDeliveryPolicy | None = None,
        start_from_now: bool = True,
    ) -> None:
        self._imap_client = imap_client
        self._notifier = notifier
        self._state_store = state_store
        self._account_key = account_key
        self._policy = policy or EmailDeliveryPolicy()
        self._start_from_now = start_from_now


    async def poll_once(self) -> int:
        last_uid = await self._state_store.get_last_uid(self._account_key)
        if last_uid == 0 and self._start_from_now:
            latest_uid = await self._imap_client.get_latest_uid()
            await self._state_store.set_last_uid(self._account_key, latest_uid)
            logger.info(
                "Bootstrap mailbox cursor at startup: account=%s last_uid=%s",
                self._account_key,
                latest_uid,
            )
            return 0

        logger.info("Polling mailbox: account=%s last_uid=%s", self._account_key, last_uid)
        new_messages = await self._imap_client.fetch_new_messages(since_uid=last_uid)
        max_uid = last_uid
        delivered = 0
        skipped = 0

        for message in new_messages:
            normalized = self._policy.normalize(message)
            if self._policy.should_deliver(normalized):
                await self._notifier.notify_email_received(normalized)
                delivered += 1
            else:
                skipped += 1
            max_uid = max(max_uid, normalized.uid)

        if max_uid != last_uid:
            await self._state_store.set_last_uid(self._account_key, max_uid)
            logger.info("Updated mailbox cursor: account=%s last_uid=%s", self._account_key, max_uid)

        logger.info(
            "Mailbox poll result: account=%s fetched=%s delivered=%s skipped=%s",
            self._account_key,
            len(new_messages),
            delivered,
            skipped,
        )

        return len(new_messages)