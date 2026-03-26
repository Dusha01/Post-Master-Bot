from src.modules.bot.application.ports.bot_state_store import BotStateStorePort


class InMemoryBotStateStore(BotStateStorePort):
    def __init__(self) -> None:
        self._paused = False

    async def set_paused(self, value: bool) -> None:
        self._paused = value

    async def is_paused(self) -> bool:
        return self._paused
