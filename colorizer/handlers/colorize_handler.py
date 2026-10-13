"""Handler for single-image colorization. Translates input -> service call."""

from __future__ import annotations

from pathlib import Path

from colorizer.services.colorize_service import ColorizeService
from colorizer.utils.paths import default_output_path


class ColorizeHandler:
    def __init__(self, service: ColorizeService) -> None:
        self._service = service

    def run(self, input_path: Path, output_path: Path | None) -> Path:
        if not input_path.is_file():
            raise FileNotFoundError(f"input image not found: {input_path}")
        dest = output_path or default_output_path(input_path)
        return self._service.colorize_file(input_path, dest)