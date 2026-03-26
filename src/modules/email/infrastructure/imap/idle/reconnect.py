class ReconnectBackoff:
    def __init__(self, base_delay_sec: float = 1.0, max_delay_sec: float = 60.0) -> None:
        self._base = base_delay_sec
        self._max = max_delay_sec
        self._attempt = 0

    def reset(self) -> None:
        self._attempt = 0

    def next_delay(self) -> float:
        delay = min(self._max, self._base * (2**self._attempt))
        self._attempt += 1
        return delay