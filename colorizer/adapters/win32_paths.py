"""Windows-specific path and shell helpers. No-ops on non-Windows."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_windows() -> bool:
    return sys.platform == "win32"


def local_app_data() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base)
    return Path.home() / "AppData" / "Local"


def reveal_in_explorer(path: Path) -> None:
    """Open Explorer with the file selected. No-op off Windows."""
    if not is_windows():
        return
    import subprocess

    subprocess.Popen(["explorer", "/select,", str(path)])  # noqa: S603,S607


def long_path_safe(path: Path) -> Path:
    """Prefix with \\\\?\\ when the path exceeds the legacy 260-char limit."""
    s = str(path)
    if is_windows() and len(s) >= 260 and not s.startswith("\\\\?\\"):
        return Path("\\\\?\\" + s)
    return path