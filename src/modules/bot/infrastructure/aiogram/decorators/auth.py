import logging
from functools import wraps
from typing import Awaitable, Callable

from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

logger = logging.getLogger(__name__)


def require_allowed_user(allowed_user_id: int) -> Callable[[Callable[[Message], Awaitable[None]]], Callable[[Message], Awaitable[None]]]:
    def decorator(handler: Callable[[Message], Awaitable[None]]) -> Callable[[Message], Awaitable[None]]:
        @wraps(handler)
        async def wrapper(message: Message, *args, **kwargs):  # type: ignore[override]
            if not message.from_user:
                return

            if message.from_user.id != allowed_user_id:
                logger.warning(
                    "Unauthorized access attempt from user_id=%s",
                    message.from_user.id,
                )
                try:
                    await message.answer("You are not authorized to use this bot.")
                except TelegramForbiddenError:
                    pass
                return

            return await handler(message, *args, **kwargs)

        return wrapper

    return decorator