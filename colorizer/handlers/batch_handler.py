"""Handler for directory batch colorization."""

from __future__ import annotations

from pathlib import Path

from colorizer.services.batch_service import BatchColorizeService, BatchResult


class BatchHandler:
    def __init__(self, service: BatchColorizeService) -> None:
        self._service = service

    def run(self, input_dir: Path, output_dir: Path, *, recursive: bool = False) -> BatchResult:
        if not input_dir.is_dir():
            raise NotADirectoryError(f"input directory not found: {input_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return self._service.colorize_directory(input_dir, output_dir, recursive=recursive)