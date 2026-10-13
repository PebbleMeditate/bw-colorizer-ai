"""Backend adapter protocol. Every inference backend implements this."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class BackendAdapter(Protocol):
    """Contract for a colorization inference backend.

    Implementations must be thread-safe: BatchColorizeService calls
    predict_ab from a thread pool.
    """

    @property
    def name(self) -> str: ...

    def predict_ab(self, gray_tensor: np.ndarray) -> np.ndarray:
        """gray_tensor: [1,1,H,W] float32 in [-1,1]. Return [1,2,H,W] a/b."""
        ...

    def warmup(self) -> None:
        """Run a dummy inference so the first real call isn't slow."""
        ...