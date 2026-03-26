from dataclasses import dataclass


@dataclass(slots=True)
class ChangeMailboxStatusCommand:
    account_key: str