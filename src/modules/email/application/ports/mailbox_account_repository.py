from abc import ABC, abstractmethod

from src.modules.email.domain.entities.mailbox_account import MailboxAccount


class MailboxAccountRepositoryPort(ABC):
    @abstractmethod
    async def save(self, account: MailboxAccount) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, account_key: str) -> MailboxAccount | None:
        raise NotImplementedError

    @abstractmethod
    async def list_active(self) -> list[MailboxAccount]:
        raise NotImplementedError