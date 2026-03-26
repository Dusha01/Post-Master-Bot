import html
import re

from src.modules.bot.application.dto.telegram_message_dto import TelegramMessageDTO
from src.modules.bot.application.ports.telegram_gateway import TelegramGatewayPort
from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class TelegramDeliveryService:
    def __init__(self, gateway: TelegramGatewayPort, default_chat_id: str) -> None:
        self._gateway = gateway
        self._default_chat_id = default_chat_id

    async def send_email_notification(self, email_message: EmailMessageDTO) -> None:
        subject = self._sanitize_line(email_message.subject)
        sender = self._sanitize_line(email_message.sender)
        provider = self._sanitize_line(email_message.provider)
        preview = self._format_preview(email_message.body_preview)
        text = (
            f"New email from {provider}\n"
            f"From: {sender}\n"
            f"Subject: {subject}\n\n"
            f"{preview}"
        )
        telegram_message = TelegramMessageDTO(chat_id=self._default_chat_id, text=text)
        await self._gateway.send_message(telegram_message)

    @staticmethod
    def _sanitize_line(value: str) -> str:
        return " ".join(value.split()).strip()

    def _format_preview(self, value: str) -> str:
        text = html.unescape(value)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return "(empty body)"
        if len(text) > 800:
            return f"{text[:797]}..."
        return text
