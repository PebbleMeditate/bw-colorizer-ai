"""Image preprocessing: decode, resize, normalize to model input tensor.

The model expects a single-channel L (grayscale) tensor in [-1, 1] at
`target_size` x `target_size`, NCHW float32. Everything here exists to
produce exactly that.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from colorizer.utils.color import rgb_to_lab_l, lab_ab_to_rgb


class PreprocessService:
    def __init__(self, *, target_size: int = 256, normalize: bool = True) -> None:
        self._target = target_size
        self._normalize = normalize

    def to_model_input(self, image: Image.Image) -> tuple[np.ndarray, tuple[int, int]]:
        """Return (tensor[1,1,H,W] float32 in [-1,1], original (w,h))."""
        original_size = image.size
        gray = image.convert("L").resize((self._target, self._target), Image.BILINEAR)
        arr = np.asarray(gray, dtype=np.float32) / 255.0
        if self._normalize:
            arr = arr * 2.0 - 1.0
        tensor = arr[None, None, :, :]
        return tensor, original_size

    def lab_to_image(self, l_channel: np.ndarray, ab_channels: np.ndarray) -> Image.Image:
        """Recombine model's predicted a/b with the original L, back to RGB."""
        rgb = lab_ab_to_rgb(l_channel, ab_channels)
        return Image.fromarray(rgb, mode="RGB")

    @staticmethod
    def ensure_grayscale(image: Image.Image) -> Image.Image:
        """Collapse any input to L so already-color images don't confuse the model."""
        return image.convert("L") if image.mode != "L" else image

    @staticmethod
    def from_rgb(image: Image.Image) -> np.ndarray:
        return np.asarray(rgb_to_lab_l(image), dtype=np.float32)