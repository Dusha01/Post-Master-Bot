from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseModel):
    bot_token: str
    chat_id: str
    retry_base_sec: float = 3.0
    retry_max_sec: float = 60.0
    allow_user_id: int
    proxy_url: str | None = None


class ImapProviderSettings(BaseModel):
    server: str
    port: int
    username: str
    password: str
    use_ssl: bool = True


class ImapSettings(BaseModel):
    gmail: ImapProviderSettings
    yandex: ImapProviderSettings
    idle_timeout_sec: int = 60


class Config(BaseSettings):
    APP_NAME: str = "Post-Master-Bot"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8050
    LANGUAGE: str = "ru"

    TELEGRAM_BOT_TOKEN: str
    CHAT_ID: str
    TG_RETRY_BASE_SEC: float = 3.0
    TG_RETRY_MAX_SEC: float = 60.0
    ALLOW_USER_ID: int
    TG_PROXY_URL: str | None = None

    IMAP_SERVER_GMAIL: str = "imap.gmail.com"
    IMAP_PORT_GMAIL: int = 993
    IMAP_USERNAME_GMAIL: str = ""
    IMAP_PASSWORD_GMAIL: str = ""
    IMAP_USE_SSL_GMAIL: bool = True

    IMAP_SERVER_YANDEX: str = "imap.yandex.ru"
    IMAP_PORT_YANDEX: int = 993
    IMAP_USERNAME_YANDEX: str = ""
    IMAP_PASSWORD_YANDEX: str = ""
    IMAP_USE_SSL_YANDEX: bool = True
    IMAP_IDLE_TIMEOUT_SEC: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def telegram(self) -> TelegramSettings:
        return TelegramSettings(
            bot_token=self.TELEGRAM_BOT_TOKEN,
            chat_id=self.CHAT_ID,
            retry_base_sec=self.TG_RETRY_BASE_SEC,
            retry_max_sec=self.TG_RETRY_MAX_SEC,
            allow_user_id=self.ALLOW_USER_ID,
            proxy_url=self.TG_PROXY_URL or None,
        )

    @property
    def imap(self) -> ImapSettings:
        return ImapSettings(
            gmail=ImapProviderSettings(
                server=self.IMAP_SERVER_GMAIL,
                port=self.IMAP_PORT_GMAIL,
                username=self.IMAP_USERNAME_GMAIL,
                password=self.IMAP_PASSWORD_GMAIL,
                use_ssl=self.IMAP_USE_SSL_GMAIL,
            ),
            yandex=ImapProviderSettings(
                server=self.IMAP_SERVER_YANDEX,
                port=self.IMAP_PORT_YANDEX,
                username=self.IMAP_USERNAME_YANDEX,
                password=self.IMAP_PASSWORD_YANDEX,
                use_ssl=self.IMAP_USE_SSL_YANDEX,
            ),
            idle_timeout_sec=self.IMAP_IDLE_TIMEOUT_SEC,
        )