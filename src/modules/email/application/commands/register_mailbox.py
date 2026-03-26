from dataclasses import dataclass


@dataclass(slots=True)
class RegisterMailboxCommand:
    provider: str
    username: str