from abc import ABC, abstractmethod


class StateStorePort(ABC):
    @abstractmethod
    async def get_last_uid(self, account_key: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def set_last_uid(self, account_key: str, uid: int) -> None:
        raise NotImplementedError
