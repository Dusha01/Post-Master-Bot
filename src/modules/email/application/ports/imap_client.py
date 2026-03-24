from abc import ABC, abstractmethod

from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class ImapClientPort(ABC):
    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def idle_wait(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def fetch_new_messages(self, *, since_uid: int) -> list[EmailMessageDTO]:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        raise NotImplementedError
