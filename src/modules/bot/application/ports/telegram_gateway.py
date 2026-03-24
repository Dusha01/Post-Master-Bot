from abc import ABC, abstractmethod

from src.modules.bot.application.dto.telegram_message_dto import TelegramMessageDTO


class TelegramGatewayPort(ABC):
    @abstractmethod
    async def send_message(self, message: TelegramMessageDTO) -> None:
        raise NotImplementedError
