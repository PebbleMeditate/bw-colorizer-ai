"""Batch orchestration over a directory tree.

Thread pool, not process pool: the ONNX runtime releases the GIL during
inference, so threads give real parallelism without the pickling cost of
shipping PIL images across process boundaries.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from colorizer.services.colorize_service import ColorizeService
from colorizer.utils.logging import get_logger
from colorizer.utils.paths import iter_images, mirror_output_path

log = get_logger(__name__)

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


@dataclass(slots=True)
class BatchResult:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    errors: dict[Path, str] = field(default_factory=dict)


class BatchColorizeService:
    def __init__(self, *, colorize: ColorizeService, max_workers: int = 4) -> None:
        self._colorize = colorize
        self._max_workers = max(1, max_workers)

    def colorize_directory(
        self, input_dir: Path, output_dir: Path, *, recursive: bool = False
    ) -> BatchResult:
        images = list(iter_images(input_dir, _IMAGE_SUFFIXES, recursive=recursive))
        result = BatchResult(total=len(images))
        if not images:
            log.warning("no images found under %s", input_dir)
            return result

        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            futures = {
                pool.submit(self._one, src, input_dir, output_dir): src for src in images
            }
            for fut in as_completed(futures):
                src = futures[fut]
                try:
                    fut.result()
                    result.succeeded += 1
                except Exception as exc:  # keep the batch alive on per-file failure
                    result.failed += 1
                    result.errors[src] = str(exc)
                    log.error("failed %s: %s", src.name, exc)
        return result

    def _one(self, src: Path, root: Path, out_root: Path) -> Path:
        dest = mirror_output_path(src, root, out_root)
        return self._colorize.colorize_file(src, dest)