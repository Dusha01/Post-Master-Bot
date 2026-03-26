from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EmailMessageDTO:
    uid: int
    provider: str
    message_id: str
    subject: str
    sender: str
    received_at: datetime
    body_preview: str