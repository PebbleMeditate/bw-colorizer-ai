"""Model registry: resolve model id -> local weight path, verify checksum.

Weights are pulled from a pinned Hugging Face revision and cached under
`cache_dir`. Every entry carries a SHA-256; a mismatch is fatal because a
tampered ONNX file is a code-execution surface for the runtime.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from colorizer.utils.logging import get_logger

log = get_logger(__name__)

_CHUNK = 1 << 20  # 1 MiB


@dataclass(frozen=True, slots=True)
class ModelSpec:
    model_id: str
    revision: str
    filename: str
    sha256: str
    input_channels: int = 1
    output_channels: int = 2


_REGISTRY: dict[str, ModelSpec] = {
    "bw-colorizer-ai/zhang-ecCV16-onnx": ModelSpec(
        model_id="bw-colorizer-ai/zhang-ecCV16-onnx",
        revision="v0.4.2",
        filename="colorizer_ecCV16.onnx",
        sha256="9f2c1a7d4b8e0f36a1c5d9e2b7f04a8c3d6e1f90b2a4c7e5d8f0136a9b2c4e70",
    ),
}


class ModelRegistry:
    def __init__(self, *, cache_dir: Path) -> None:
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def resolve(self, model_id: str) -> Path:
        spec = _REGISTRY.get(model_id)
        if spec is None:
            raise KeyError(f"unknown model id: {model_id}")
        target = self._cache_dir / spec.revision / spec.filename
        if not target.exists():
            self._download(spec, target)
        self._verify(spec, target)
        return target

    def _download(self, spec: ModelSpec, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/{spec.model_id}/resolve/{spec.revision}/{spec.filename}"
        log.info("downloading %s -> %s", url, target)
        import urllib.request

        with urllib.request.urlopen(url) as resp, target.open("wb") as fh:  # noqa: S310
            while chunk := resp.read(_CHUNK):
                fh.write(chunk)

    def _verify(self, spec: ModelSpec, target: Path) -> None:
        digest = hashlib.sha256()
        with target.open("rb") as fh:
            while chunk := fh.read(_CHUNK):
                digest.update(chunk)
        actual = digest.hexdigest()
        if actual != spec.sha256:
            target.unlink(missing_ok=True)
            raise RuntimeError(
                f"checksum mismatch for {spec.filename}: expected {spec.sha256[:12]}…, "
                f"got {actual[:12]}… — file removed, refusing to load"
            )