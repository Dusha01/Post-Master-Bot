from abc import ABC, abstractmethod

from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class NotifierPort(ABC):
    @abstractmethod
    async def notify_email_received(self, message: EmailMessageDTO) -> None:
        raise NotImplementedError