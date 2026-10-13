"""CLI entry point. Thin — parses args, hands off to handlers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from colorizer.bootstrap.container import build_container
from colorizer.config.settings import Settings
from colorizer.handlers.colorize_handler import ColorizeHandler
from colorizer.handlers.batch_handler import BatchHandler
from colorizer.utils.logging import get_logger

log = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bw-colorizer", description="AI colorizer: B&W to color")
    sub = p.add_subparsers(dest="command", required=True)

    single = sub.add_parser("colorize", help="Colorize a single image")
    single.add_argument("input", type=Path)
    single.add_argument("-o", "--output", type=Path, default=None)
    single.add_argument("--model", default=None, help="Override model id")
    single.add_argument("--device", choices=["cpu", "cuda", "dml"], default=None)

    batch = sub.add_parser("batch", help="Colorize a directory of images")
    batch.add_argument("input_dir", type=Path)
    batch.add_argument("-o", "--output-dir", type=Path, required=True)
    batch.add_argument("--workers", type=int, default=None)
    batch.add_argument("--recursive", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = Settings.from_env()
    if getattr(args, "model", None):
        settings = settings.merge(model_id=args.model)
    if getattr(args, "device", None):
        settings = settings.merge(onnx_providers=Settings.providers_for(args.device))

    container = build_container(settings)

    if args.command == "colorize":
        handler = ColorizeHandler(container.colorize)
        out = handler.run(args.input, args.output)
        log.info("wrote %s", out)
        return 0

    if args.command == "batch":
        handler = BatchHandler(container.batch)
        result = handler.run(args.input_dir, args.output_dir, recursive=args.recursive)
        log.info("colorized %d/%d", result.succeeded, result.total)
        return 0 if result.failed == 0 else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())