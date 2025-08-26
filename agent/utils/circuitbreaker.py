from __future__ import annotations
import time, os

MAX_STEPS = int(os.getenv("MAX_STEPS", "12"))
MAX_RUN_SEC = int(os.getenv("MAX_RUN_SEC", "30"))

class CircuitBreaker:
    def __init__(self, max_steps: int = MAX_STEPS, max_seconds: int = MAX_RUN_SEC):
        self.max_steps = max_steps
        self.max_seconds = max_seconds
        self._steps = 0
        self._t0 = time.time()

    def hit(self) -> None:
        self._steps += 1

    def should_break(self) -> bool:
        if self._steps >= self.max_steps:
            return True
        if (time.time() - self._t0) > self.max_seconds:
            return True
        return False
