from dataclasses import dataclass


@dataclass(slots=True)
class DeliveryMessage:
    chat_id: str
    text: str
    parse_mode: str | None = None
