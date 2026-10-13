"""Dependency container. Wires adapters -> services -> handlers.

Kept deliberately dumb: no magic, no auto-discovery. Every dependency is
constructed explicitly so the wiring graph is readable top-to-bottom.
"""

from __future__ import annotations

from dataclasses import dataclass

from colorizer.adapters.onnx_backend import OnnxBackend
from colorizer.config.settings import Settings
from colorizer.models.registry import ModelRegistry
from colorizer.services.batch_service import BatchColorizeService
from colorizer.services.colorize_service import ColorizeService
from colorizer.services.preprocess_service import PreprocessService
from colorizer.utils.logging import configure_logging


@dataclass(slots=True)
class Container:
    settings: Settings
    registry: ModelRegistry
    preprocess: PreprocessService
    colorize: ColorizeService
    batch: BatchColorizeService


def build_container(settings: Settings) -> Container:
    configure_logging(settings.log_level)
    registry = ModelRegistry(cache_dir=settings.model_cache_dir)
    backend = OnnxBackend(
        registry=registry,
        model_id=settings.model_id,
        providers=settings.onnx_providers,
    )
    preprocess = PreprocessService(
        target_size=settings.input_size,
        normalize=settings.normalize_input,
    )
    colorize = ColorizeService(backend=backend, preprocess=preprocess)
    batch = BatchColorizeService(colorize=colorize, max_workers=settings.batch_workers)
    return Container(
        settings=settings,
        registry=registry,
        preprocess=preprocess,
        colorize=colorize,
        batch=batch,
    )