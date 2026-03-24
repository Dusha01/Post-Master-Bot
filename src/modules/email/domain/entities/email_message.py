from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EmailMessage:
    message_id: str
    subject: str
    sender: str
    received_at: datetime
    body_text: str
