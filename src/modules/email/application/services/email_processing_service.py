from src.modules.email.application.ports.imap_client import ImapClientPort
from src.modules.email.application.ports.notifier import NotifierPort
from src.modules.email.application.ports.state_store import StateStorePort


class EmailProcessingService:
    def __init__(
        self,
        imap_client: ImapClientPort,
        notifier: NotifierPort,
        state_store: StateStorePort,
        account_key: str,
    ) -> None:
        self._imap_client = imap_client
        self._notifier = notifier
        self._state_store = state_store
        self._account_key = account_key

    async def poll_once(self) -> int:
        last_uid = await self._state_store.get_last_uid(self._account_key)
        new_messages = await self._imap_client.fetch_new_messages(since_uid=last_uid)
        max_uid = last_uid

        for message in new_messages:
            await self._notifier.notify_email_received(message)
            uid = self._extract_uid(message.message_id, fallback=max_uid)
            max_uid = max(max_uid, uid)

        if max_uid != last_uid:
            await self._state_store.set_last_uid(self._account_key, max_uid)

        return len(new_messages)

    @staticmethod
    def _extract_uid(message_id: str, fallback: int) -> int:
        try:
            return int(message_id)
        except ValueError:
            return fallback
