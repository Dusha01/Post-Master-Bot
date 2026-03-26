import logging

from src.core.config import Config
from src.core.container import AppContainer, build_container
from src.core.logging import setup_logging
from src.modules.bot.presentation.telegram import register_routers

logger = logging.getLogger(__name__)


async def startup() -> AppContainer:
    config = Config()
    setup_logging(debug=config.DEBUG)
    logger.info("Logging is configured")
    container = await build_container()
    register_routers(
        container.dispatcher,
        container.bot_control_service,
        container.config.telegram.allow_user_id,
    )
    logger.info("Telegram routers registered")
    return container
