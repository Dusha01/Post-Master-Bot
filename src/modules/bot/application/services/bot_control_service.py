from src.modules.bot.application.ports.bot_state_store import BotStateStorePort


class BotControlService:
    def __init__(self, state_store: BotStateStorePort) -> None:
        self._state_store = state_store

    async def pause(self) -> None:
        await self._state_store.set_paused(True)

    async def resume(self) -> None:
        await self._state_store.set_paused(False)

    async def status_text(self) -> str:
        paused = await self.is_paused()
        return "Bot status: paused" if paused else "Bot status: active"

    async def is_paused(self) -> bool:
        return await self._state_store.is_paused()
