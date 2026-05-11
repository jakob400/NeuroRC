"""Fixed-depth ring buffer for delayed voltage lookups.

Holds the most recent `depth` per-neuron voltage vectors so delay() can
read any of them in O(1) without traversing the full simulation history.
NUM-5 extends this with linear interpolation between adjacent slices.
"""

import numpy as np


class RingBuffer:
    def __init__(self, N: int, depth: int, fill: float = 0.0):
        if depth < 1:
            raise ValueError("depth must be >= 1")
        self._buf = np.full((depth, N), fill, dtype=np.float64)
        self._N = N
        self._depth = depth
        self._next = 0       # next write position
        self._count = 0      # total pushes (saturates at depth)

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def filled(self) -> int:
        return min(self._count, self._depth)

    def push(self, vec: np.ndarray) -> None:
        self._buf[self._next] = vec
        self._next = (self._next + 1) % self._depth
        self._count += 1

    def at(self, steps_back: int) -> np.ndarray:
        """Return the vector pushed `steps_back` ago. 0 = most recent."""
        if steps_back < 0:
            raise ValueError("steps_back must be >= 0")
        bound = max(self.filled - 1, 0)
        if steps_back > bound:
            steps_back = bound
        idx = (self._next - 1 - steps_back) % self._depth
        return self._buf[idx]
