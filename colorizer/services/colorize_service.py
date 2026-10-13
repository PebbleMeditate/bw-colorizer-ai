"""Core colorization service. Backend-agnostic.

Orchestrates: load image -> preprocess -> backend inference -> recombine
-> save. Knows nothing about ONNX, Torch, or which GUI called it.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from colorizer.adapters.base import BackendAdapter
from colorizer.services.preprocess_service import PreprocessService
from colorizer.utils.logging import get_logger

log = get_logger(__name__)


class ColorizeService:
    def __init__(self, *, backend: BackendAdapter, preprocess: PreprocessService) -> None:
        self._backend = backend
        self._preprocess = preprocess

    def colorize_file(self, input_path: Path, output_path: Path) -> Path:
        with Image.open(input_path) as raw:
            raw.load()
            result = self.colorize_image(raw)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.save(output_path, format="PNG")
        log.debug("colorized %s -> %s", input_path.name, output_path.name)
        return output_path

    def colorize_image(self, image: Image.Image) -> Image.Image:
        gray = self._preprocess.ensure_grayscale(image)
        tensor, original_size = self._preprocess.to_model_input(gray)
        ab = self._backend.predict_ab(tensor)  # [1,2,H,W] in [-1,1]
        l_channel = self._preprocess.from_rgb(gray)
        result = self._preprocess.lab_to_image(l_channel, ab)
        if result.size != original_size:
            result = result.resize(original_size, Image.LANCZOS)
        return result