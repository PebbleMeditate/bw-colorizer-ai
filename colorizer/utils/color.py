"""Color space conversions. PIL's 'LAB' is L in [0,255], a/b offset by 128."""

from __future__ import annotations

import numpy as np
from PIL import Image

_LAB_OFFSET = 128.0


def rgb_to_lab_l(image: Image.Image) -> np.ndarray:
    """Return the L channel of an RGB image, float32 in [0, 255]."""
    lab = np.asarray(image.convert("RGB").convert("LAB"), dtype=np.float32)
    return lab[:, :, 0]


def lab_ab_to_rgb(l_channel: np.ndarray, ab_channels: np.ndarray) -> np.ndarray:
    """Recombine L [H,W] (0..255) with a/b [2,H,W] (already in [-110,110]).

    PIL expects a/b offset by 128 to fit uint8. We add the offset, clip,
    stack with L, and convert LAB -> RGB.
    """
    a = ab_channels[0] + _LAB_OFFSET
    b = ab_channels[1] + _LAB_OFFSET
    lab = np.stack(
        [np.clip(l_channel, 0, 255), np.clip(a, 0, 255), np.clip(b, 0, 255)],
        axis=-1,
    ).astype(np.uint8)
    return np.asarray(Image.fromarray(lab, mode="LAB").convert("RGB"))