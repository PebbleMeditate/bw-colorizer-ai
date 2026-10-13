"""Runtime settings. Immutable, env-aware, mergeable.

Precedence: explicit merge() > environment > defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

_DEFAULT_MODEL = "bw-colorizer-ai/zhang-ecCV16-onnx"
_DEFAULT_CACHE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "bw-colorizer-ai" / "models"


@dataclass(frozen=True, slots=True)
class Settings:
    model_id: str = _DEFAULT_MODEL
    model_cache_dir: Path = _DEFAULT_CACHE
    input_size: int = 256
    normalize_input: bool = True
    onnx_providers: tuple[str, ...] = ("CPUExecutionProvider",)
    batch_workers: int = max(1, (os.cpu_count() or 4) // 2)
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model_id=os.environ.get("BWCOLOR_MODEL", _DEFAULT_MODEL),
            model_cache_dir=Path(os.environ.get("BWCOLOR_CACHE", _DEFAULT_CACHE)),
            input_size=int(os.environ.get("BWCOLOR_INPUT_SIZE", "256")),
            batch_workers=int(os.environ.get("BWCOLOR_WORKERS", str(cls().batch_workers))),
            log_level=os.environ.get("BWCOLOR_LOG", "INFO"),
        )

    def merge(self, **overrides: object) -> "Settings":
        return replace(self, **overrides)  # type: ignore[arg-type]

    @staticmethod
    def providers_for(device: str) -> tuple[str, ...]:
        return {
            "cpu": ("CPUExecutionProvider",),
            "cuda": ("CUDAExecutionProvider", "CPUExecutionProvider"),
            "dml": ("DmlExecutionProvider", "CPUExecutionProvider"),
        }[device]