from src.core.container import AppContainer, build_container
from src.core.logging import setup_logging


def startup() -> AppContainer:
    container = build_container()
    setup_logging(debug=container.config.DEBUG)
    return container
