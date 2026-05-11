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


def interpolated_lookup(buf: 'RingBuffer', dt_list, tau_D):
    """Linear interpolation at lag tau_D into the past.

    buf.at(0) is the most recent push. dt_list[-1] is the dt of the most
    recent step. Walk back accumulating dt until the running sum brackets
    tau_D, then linearly interpolate between buf.at(i) and buf.at(i+1).
    """
    dt_sum = 0.0
    n = len(dt_list)
    for i in range(n):
        step = dt_list[-i - 1]
        new_sum = dt_sum + step
        if new_sum >= tau_D:
            alpha = (tau_D - dt_sum) / step if step > 0 else 0.0
            return (1.0 - alpha) * buf.at(i) + alpha * buf.at(i + 1)
        dt_sum = new_sum
    # History too short; return oldest available
    return buf.at(min(buf.filled - 1, buf.depth - 1))
