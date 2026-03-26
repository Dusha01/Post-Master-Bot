import logging

from aiogram import Bot

from src.modules.bot.application.dto.telegram_message_dto import TelegramMessageDTO
from src.modules.bot.application.ports.telegram_gateway import TelegramGatewayPort

logger = logging.getLogger(__name__)


class AiogramTelegramGateway(TelegramGatewayPort):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send_message(self, message: TelegramMessageDTO) -> None:
        logger.info(
            "Sending Telegram message: chat_id=%s parse_mode=%s length=%s",
            message.chat_id,
            message.parse_mode,
            len(message.text),
        )
        await self._bot.send_message(
            chat_id=message.chat_id,
            text=message.text,
            parse_mode=message.parse_mode,
        )
        logger.info("Telegram message sent: chat_id=%s", message.chat_id)
