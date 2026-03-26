from src.modules.email.application.ports.state_store import StateStorePort


class InMemoryStateStore(StateStorePort):
    def __init__(self) -> None:
        self._state: dict[str, int] = {}

    async def get_last_uid(self, account_key: str) -> int:
        return self._state.get(account_key, 0)

    async def set_last_uid(self, account_key: str, uid: int) -> None:
        self._state[account_key] = uid
