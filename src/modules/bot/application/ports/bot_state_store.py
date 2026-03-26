from abc import ABC, abstractmethod


class BotStateStorePort(ABC):
    @abstractmethod
    async def set_paused(self, value: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_paused(self) -> bool:
        raise NotImplementedError
