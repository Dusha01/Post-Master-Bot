from src.modules.email.application.ports.mailbox_account_repository import MailboxAccountRepositoryPort
from src.modules.email.domain.entities.mailbox_account import MailboxAccount


class InMemoryMailboxAccountRepository(MailboxAccountRepositoryPort):
    def __init__(self) -> None:
        self._accounts: dict[str, MailboxAccount] = {}

    async def save(self, account: MailboxAccount) -> None:
        self._accounts[account.key] = account

    async def get(self, account_key: str) -> MailboxAccount | None:
        return self._accounts.get(account_key)

    async def list_active(self) -> list[MailboxAccount]:
        return [account for account in self._accounts.values() if account.is_active]