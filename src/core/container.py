from dataclasses import dataclass

from src.core.config import Config


@dataclass(slots=True)
class AppContainer:
    config: Config


def build_container() -> AppContainer:
    return AppContainer(config=Config())
