from src.modules.bot.application.dto.telegram_message_dto import TelegramMessageDTO
from src.modules.bot.application.ports.telegram_gateway import TelegramGatewayPort
from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class TelegramDeliveryService:
    def __init__(self, gateway: TelegramGatewayPort, default_chat_id: str) -> None:
        self._gateway = gateway
        self._default_chat_id = default_chat_id

    async def send_email_notification(self, email_message: EmailMessageDTO) -> None:
        text = (
            f"New email from {email_message.provider}\n"
            f"From: {email_message.sender}\n"
            f"Subject: {email_message.subject}\n\n"
            f"{email_message.body_preview}"
        )
        telegram_message = TelegramMessageDTO(chat_id=self._default_chat_id, text=text)
        await self._gateway.send_message(telegram_message)
