from src.modules.email.application.ports.imap_client import ImapClientPort
from src.modules.email.application.ports.mailbox_account_repository import MailboxAccountRepositoryPort
from src.modules.email.application.ports.notifier import NotifierPort
from src.modules.email.application.ports.state_store import StateStorePort
from src.modules.email.application.services.email_processing_service import EmailProcessingService
from src.modules.email.domain.policies.email_delivery_policy import EmailDeliveryPolicy


class PollActiveMailboxesUseCase:
    def __init__(
        self,
        repository: MailboxAccountRepositoryPort,
        state_store: StateStorePort,
        notifier: NotifierPort,
        policy: EmailDeliveryPolicy | None = None,
    ) -> None:
        self._repository = repository
        self._state_store = state_store
        self._notifier = notifier
        self._policy = policy or EmailDeliveryPolicy()

    async def execute(self, clients: dict[str, ImapClientPort]) -> dict[str, int]:
        result: dict[str, int] = {}
        active_accounts = await self._repository.list_active()

        for account in active_accounts:
            client = clients.get(account.key)
            if client is None:
                continue

            service = EmailProcessingService(
                imap_client=client,
                notifier=self._notifier,
                state_store=self._state_store,
                account_key=account.key,
                policy=self._policy,
            )
            result[account.key] = await service.poll_once()

        return result