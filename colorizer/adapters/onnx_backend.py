"""ONNX Runtime backend. Primary backend on Windows.

Uses a per-thread session via thread-local storage because ORT sessions
are not guaranteed reentrant across threads in every provider.
"""

from __future__ import annotations

import threading

import numpy as np
import onnxruntime as ort

from colorizer.models.registry import ModelRegistry
from colorizer.models.tensor_ops import denormalize_ab, squeeze_batch
from colorizer.utils.logging import get_logger

log = get_logger(__name__)


class OnnxBackend:
    def __init__(
        self,
        *,
        registry: ModelRegistry,
        model_id: str,
        providers: tuple[str, ...],
    ) -> None:
        self._registry = registry
        self._model_id = model_id
        self._providers = list(providers)
        self._local = threading.local()
        self._input_name: str | None = None
        self._output_name: str | None = None

    @property
    def name(self) -> str:
        return f"onnx:{self._model_id}"

    def _session(self) -> ort.InferenceSession:
        session = getattr(self._local, "session", None)
        if session is not None:
            return session
        path = self._registry.resolve(self._model_id)
        session = ort.InferenceSession(str(path), providers=self._providers)
        self._input_name = session.get_inputs()[0].name
        self._output_name = session.get_outputs()[0].name
        self._local.session = session
        log.info("loaded onnx session providers=%s", session.get_providers())
        return session

    def predict_ab(self, gray_tensor: np.ndarray) -> np.ndarray:
        session = self._session()
        assert self._input_name is not None and self._output_name is not None
        out = session.run([self._output_name], {self._input_name: gray_tensor})[0]
        return denormalize_ab(out.astype(np.float32))

    def warmup(self) -> None:
        session = self._session()
        assert self._input_name is not None
        dummy = np.zeros((1, 1, 256, 256), dtype=np.float32)
        session.run([self._output_name], {self._input_name: dummy})

    def predict_ab_single(self, gray_tensor: np.ndarray) -> np.ndarray:
        """Convenience for callers that want the [2,H,W] shape directly."""
        return squeeze_batch(self.predict_ab(gray_tensor))