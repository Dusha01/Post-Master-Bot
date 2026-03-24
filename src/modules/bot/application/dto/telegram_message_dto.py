from dataclasses import dataclass


@dataclass(slots=True)
class TelegramMessageDTO:
    chat_id: str
    text: str
    parse_mode: str | None = None
