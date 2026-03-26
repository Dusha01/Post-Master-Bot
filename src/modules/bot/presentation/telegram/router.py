from aiogram import Dispatcher

from src.modules.bot.application.services.bot_control_service import BotControlService
from src.modules.bot.infrastructure.aiogram.handlers.system_handlers import (
    build_system_router,
)


def register_routers(
    dispatcher: Dispatcher,
    control_service: BotControlService,
    allowed_user_id: int,
) -> None:
    dispatcher.include_router(build_system_router(control_service, allowed_user_id))
