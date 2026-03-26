import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.modules.bot.application.services.bot_control_service import BotControlService
from src.modules.bot.infrastructure.aiogram.decorators.auth import require_allowed_user

logger = logging.getLogger(__name__)


def build_system_router(control_service: BotControlService, allowed_user_id: int) -> Router:
    router = Router(name="system")

    @router.message(Command("start"))
    @require_allowed_user(allowed_user_id)
    async def start_handler(message: Message) -> None:
        logger.info("Command /start from user_id=%s", message.from_user.id if message.from_user else "unknown")
        await message.answer(
            "Post-Master-Bot is running.\n"
            "Available commands:\n"
            "/status - show current status\n"
            "/pause - pause forwarding\n"
            "/resume - resume forwarding"
        )

    @router.message(Command("status"))
    @require_allowed_user(allowed_user_id)
    async def status_handler(message: Message) -> None:
        logger.info("Command /status from user_id=%s", message.from_user.id if message.from_user else "unknown")
        await message.answer(await control_service.status_text())

    @router.message(Command("pause"))
    @require_allowed_user(allowed_user_id)
    async def pause_handler(message: Message) -> None:
        logger.info("Command /pause from user_id=%s", message.from_user.id if message.from_user else "unknown")
        await control_service.pause()
        await message.answer("Forwarding paused.")

    @router.message(Command("resume"))
    @require_allowed_user(allowed_user_id)
    async def resume_handler(message: Message) -> None:
        logger.info("Command /resume from user_id=%s", message.from_user.id if message.from_user else "unknown")
        await control_service.resume()
        await message.answer("Forwarding resumed.")

    return router