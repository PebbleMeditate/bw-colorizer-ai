"""Path helpers: output naming, image discovery, directory mirroring."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}.colorized.png")


def iter_images(root: Path, suffixes: set[str], *, recursive: bool) -> Iterator[Path]:
    pattern = "**/*" if recursive else "*"
    for path