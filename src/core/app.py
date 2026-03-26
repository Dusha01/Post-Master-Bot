import asyncio
import logging

from aiogram.exceptions import TelegramNetworkError

from src.core.container import AppContainer
from src.core.startup import startup

logger = logging.getLogger(__name__)


class BotApplication:
    def __init__(self, container: AppContainer) -> None:
        self._container = container

    async def run(self) -> None:
        delay = max(0.5, self._container.config.telegram.retry_base_sec)
        max_delay = max(delay, self._container.config.telegram.retry_max_sec)
        worker_tasks = [asyncio.create_task(worker.run()) for worker in self._container.email_workers]
        if worker_tasks:
            logger.info("Started email workers: count=%s", len(worker_tasks))
        else:
            logger.warning("No email workers started. Check IMAP credentials in .env")
        logger.info("Starting Telegram polling loop")
        try:
            while True:
                try:
                    logger.info("Attempting to connect to Telegram polling")
                    await self._container.dispatcher.start_polling(self._container.bot)
                    logger.info("Telegram polling stopped gracefully")
                    break
                except TelegramNetworkError as exc:
                    logger.warning(
                        "Telegram network error, retry in %.1fs: %s",
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)
                    delay = min(max_delay, delay * 2)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("Unhandled error in polling loop, retry in %.1fs", delay)
                    await asyncio.sleep(delay)
                    delay = min(max_delay, delay * 2)
        finally:
            for worker in self._container.email_workers:
                worker.stop()
            for task in worker_tasks:
                task.cancel()
            if worker_tasks:
                await asyncio.gather(*worker_tasks, return_exceptions=True)
            logger.info("Closing Telegram bot session")
            await self._container.bot.session.close()


async def create_app() -> BotApplication:
    container = await startup()
    return BotApplication(container)
