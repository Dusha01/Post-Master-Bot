from dataclasses import dataclass


@dataclass(slots=True)
class MailboxAccount:
    provider: str
    username: str
    is_active: bool = True
    last_uid: int = 0

    @property
    def key(self) -> str:
        return f"{self.provider}:{self.username}"

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False