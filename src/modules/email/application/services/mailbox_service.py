from src.modules.email.application.ports.mailbox_account_repository import MailboxAccountRepositoryPort
from src.modules.email.domain.entities.mailbox_account import MailboxAccount


class MailboxService:
    def __init__(self, repository: MailboxAccountRepositoryPort) -> None:
        self._repository = repository

    async def register(self, provider: str, username: str) -> MailboxAccount:
        account = MailboxAccount(provider=provider, username=username, is_active=True)
        await self._repository.save(account)
        return account

    async def start(self, account_key: str) -> MailboxAccount | None:
        account = await self._repository.get(account_key)
        if account is None:
            return None
        account.activate()
        await self._repository.save(account)
        return account

    async def stop(self, account_key: str) -> MailboxAccount | None:
        account = await self._repository.get(account_key)
        if account is None:
            return None
        account.deactivate()
        await self._repository.save(account)
        return account

    async def list_active(self) -> list[MailboxAccount]:
        return await self._repository.list_active()