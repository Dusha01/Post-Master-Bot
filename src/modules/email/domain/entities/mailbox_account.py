from dataclasses import dataclass


@dataclass(slots=True)
class MailboxAccount:
    provider: str
    username: str
    is_active: bool = True
    last_uid: int = 0
