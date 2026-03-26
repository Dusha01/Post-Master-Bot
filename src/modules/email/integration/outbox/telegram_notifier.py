import logging

from src.modules.bot.application.services.bot_control_service import BotControlService
from src.modules.bot.application.services.telegram_delivery_service import (
    TelegramDeliveryService,
)
from src.modules.email.application.dto.email_message_dto import EmailMessageDTO
from src.modules.email.application.ports.notifier import NotifierPort

logger = logging.getLogger(__name__)


class TelegramNotifierAdapter(NotifierPort):
    def __init__(
        self,
        delivery_service: TelegramDeliveryService,
        control_service: BotControlService,
    ) -> None:
        self._delivery_service = delivery_service
        self._control_service = control_service

    async def notify_email_received(self, message: EmailMessageDTO) -> None:
        if await self._control_service.is_paused():
            logger.info(
                "Skip Telegram notify because bot is paused: provider=%s uid=%s",
                message.provider,
                message.uid,
            )
            return
        logger.info(
            "Forwarding email to Telegram: provider=%s uid=%s subject=%r",
            message.provider,
            message.uid,
            message.subject,
        )
        try:
            await self._delivery_service.send_email_notification(message)
        except Exception:
            logger.exception(
                "Failed to forward email to Telegram: provider=%s uid=%s",
                message.provider,
                message.uid,
            )
