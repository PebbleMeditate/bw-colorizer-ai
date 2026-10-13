"""Small tensor helpers shared by backends. Kept numpy-only, no framework."""

from __future__ import annotations

import numpy as np

_AB_CLAMP = 1.0


def denormalize_ab(ab: np.ndarray) -> np.ndarray:
    """Model emits a/b in [-1, 1]; LAB a/b live in roughly [-128, 127].

    Scale to the classic [-110, 110] colorization range and clamp so a
    slightly out-of-range prediction can't produce neon garbage.
    """
    scaled = ab * 110.0
    return np.clip(scaled, -110.0, 110.0)


def squeeze_batch(tensor: np.ndarray) -> np.ndarray:
    """Drop the leading batch dim if present: [1,C,H,W] -> [C,H,W]."""
    if tensor.ndim == 4 and tensor.shape[0] == 1:
        return tensor[0]
    return tensor