# Contributing to bw-colorizer-ai

Thanks for wanting to help colorize the world. This repo is a Windows
desktop tool that takes black-and-white photos and pushes them through a
learned colorization model. Contributions of all sizes are welcome —
model swaps, adapter ports, GUI polish, test coverage.

## Ground rules

- Python 3.11+ is the floor. We target 3.11 and 3.12 on Windows 10/11 x64.
- Every PR runs `ruff`, `mypy --strict` on `colorizer/`, and `pytest`.
- No model weights in git. Ever. Weights download at first run into
  `models/cache/` and are checksum-verified in `models/registry.py`.
- Keep handlers thin. Business logic lives in `services/`. If your
  handler is longer than ~40 lines, it belongs in a service.

## Layout

```
colorizer/
  bootstrap/      # app entry, DI wiring, lifecycle
  handlers/       # thin CLI + GUI command handlers
  services/       # business logic (colorize, batch, preprocess)
  models/         # model registry, weight loading, tensor adapters
  adapters/       # platform + backend adapters (ONNX, Torch, Win32)
  utils/          # image IO, color space, logging, paths
  config/         # settings schema + defaults
tests/            # pytest, mirrors colorizer/ structure
```

## Dev setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
```

## Style

- Type hints everywhere. `mypy --strict` is the bar.
- Prefer `pathlib.Path` over string paths.
- Log with `logging.getLogger(__name__)`, never `print`.
- New backend? Implement `adapters.base.BackendAdapter` and register it.

## Commit messages

Conventional-ish: `feat(services): batch colorize with progress`,
`fix(adapters): onnx provider fallback on CPU-only hosts`.

## Reporting bugs

Open an issue with: Windows version, Python version, GPU/CPU, the input
image dimensions, and the full traceback. Attach the input if it's not
private. Colorization bugs are almost always model/input issues — the
traceback plus the input image resolves 90% of them.