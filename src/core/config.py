from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):

    APP_NAME: str="Post-Master-Bot"
    DEBUG: bool = False


    HOST: str = "0.0.0.0"
    PORT: int = 8050


    TELEGRAM_BOT_TOKEN: str
    CHAT_ID: str

    smtp_server_gmail: str = ""
    smtp_port_gmail: int = 587
    smtp_username_gmail: str = ""
    smtp_password_gmail: str = ""
    smtp_use_tls: bool = True


    LANGUAGE: str = "ru"


    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

