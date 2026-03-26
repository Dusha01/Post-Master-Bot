from src.core.config import ImapProviderSettings
from src.modules.email.infrastructure.imap.clients.imap_idle_client import ImapIdleClient


class YandexImapClient(ImapIdleClient):
    def __init__(self, settings: ImapProviderSettings, idle_timeout_sec: int = 60) -> None:
        super().__init__(provider="yandex", settings=settings, idle_timeout_sec=idle_timeout_sec)