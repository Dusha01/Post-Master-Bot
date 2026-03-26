from dataclasses import dataclass
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from src.core.config import Config
from src.modules.bot.application.services.bot_control_service import BotControlService
from src.modules.bot.application.services.telegram_delivery_service import (
    TelegramDeliveryService,
)
from src.modules.bot.infrastructure.aiogram.telegram_gateway import AiogramTelegramGateway
from src.modules.bot.infrastructure.repositories.in_memory_bot_state_store import (
    InMemoryBotStateStore,
)
from src.modules.email.application.services.email_processing_service import (
    EmailProcessingService,
)
from src.modules.email.application.services.mailbox_service import MailboxService
from src.modules.email.infrastructure.imap.idle.idle_worker import ImapIdleWorker
from src.modules.email.infrastructure.imap.clients.gmail_client import GmailImapClient
from src.modules.email.infrastructure.imap.clients.yandex_client import YandexImapClient
from src.modules.email.infrastructure.repositories.in_memory_mailbox_account_repository import (
    InMemoryMailboxAccountRepository,
)
from src.modules.email.infrastructure.repositories.in_memory_state_store import InMemoryStateStore
from src.modules.email.integration.outbox.telegram_notifier import TelegramNotifierAdapter

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AppContainer:
    config: Config
    bot: Bot
    dispatcher: Dispatcher
    bot_control_service: BotControlService
    telegram_delivery_service: TelegramDeliveryService
    email_workers: list[ImapIdleWorker]


async def build_container() -> AppContainer:
    config = Config()
    logger.info("Loading configuration: app=%s debug=%s", config.APP_NAME, config.DEBUG)
    session = AiohttpSession(proxy=config.telegram.proxy_url) if config.telegram.proxy_url else None
    bot = Bot(token=config.telegram.bot_token, session=session)
    dispatcher = Dispatcher()
    logger.info(
        "Telegram client initialized: chat_id=%s token_mask=%s...",
        config.telegram.chat_id,
        config.telegram.bot_token[:8] if config.telegram.bot_token else "empty",
    )
    logger.info(
        "Telegram runtime: retry_base=%.1fs retry_max=%.1fs proxy=%s",
        config.telegram.retry_base_sec,
        config.telegram.retry_max_sec,
        "enabled" if config.telegram.proxy_url else "disabled",
    )
    logger.info(
        "IMAP settings loaded: gmail=%s:%s yandex=%s:%s idle_timeout=%ss",
        config.imap.gmail.server,
        config.imap.gmail.port,
        config.imap.yandex.server,
        config.imap.yandex.port,
        config.imap.idle_timeout_sec,
    )

    gateway = AiogramTelegramGateway(bot=bot)
    bot_state_store = InMemoryBotStateStore()
    bot_control_service = BotControlService(state_store=bot_state_store)
    telegram_delivery_service = TelegramDeliveryService(
        gateway=gateway,
        default_chat_id=config.telegram.chat_id,
    )
    notifier = TelegramNotifierAdapter(
        delivery_service=telegram_delivery_service,
        control_service=bot_control_service,
    )

    mailbox_repository = InMemoryMailboxAccountRepository()
    email_state_store = InMemoryStateStore()
    mailbox_service = MailboxService(repository=mailbox_repository)
    email_workers: list[ImapIdleWorker] = []

    if config.imap.gmail.username and config.imap.gmail.password:
        gmail_account = await mailbox_service.register("gmail", config.imap.gmail.username)
        gmail_client = GmailImapClient(
            settings=config.imap.gmail,
            idle_timeout_sec=config.imap.idle_timeout_sec,
        )
        gmail_processing = EmailProcessingService(
            imap_client=gmail_client,
            notifier=notifier,
            state_store=email_state_store,
            account_key=gmail_account.key,
        )
        email_workers.append(
            ImapIdleWorker(
                account_key=gmail_account.key,
                client=gmail_client,
                processing_service=gmail_processing,
            )
        )
        logger.info("Registered Gmail worker: account=%s", gmail_account.key)

    if config.imap.yandex.username and config.imap.yandex.password:
        yandex_account = await mailbox_service.register("yandex", config.imap.yandex.username)
        yandex_client = YandexImapClient(
            settings=config.imap.yandex,
            idle_timeout_sec=config.imap.idle_timeout_sec,
        )
        yandex_processing = EmailProcessingService(
            imap_client=yandex_client,
            notifier=notifier,
            state_store=email_state_store,
            account_key=yandex_account.key,
        )
        email_workers.append(
            ImapIdleWorker(
                account_key=yandex_account.key,
                client=yandex_client,
                processing_service=yandex_processing,
            )
        )
        logger.info("Registered Yandex worker: account=%s", yandex_account.key)

    logger.info("Total email workers configured: %s", len(email_workers))

    return AppContainer(
        config=config,
        bot=bot,
        dispatcher=dispatcher,
        bot_control_service=bot_control_service,
        telegram_delivery_service=telegram_delivery_service,
        email_workers=email_workers,
    )
