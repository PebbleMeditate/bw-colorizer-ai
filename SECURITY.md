# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@bw-colorizer-ai.dev` with a description, repro steps, and
the affected version. We aim to acknowledge within 72 hours and ship a
patch within 14 days for confirmed issues.

Please do not open public issues for security bugs.

## Threat model — what this tool touches

`bw-colorizer-ai` is a local desktop tool. It reads image files, runs
them through an ONNX/Torch colorization model, and writes output images.
It does not open sockets, does not phone home, and does not upload user
images anywhere.

Areas we care about:

- **Model weight integrity.** Weights are downloaded from a pinned
  Hugging Face revision and verified against a SHA-256 recorded in
  `models/registry.py`. A tampered weight file is a code-execution
  vector for the ONNX/Torch runtime — treat checksum mismatches as
  fatal and refuse to load.
- **Image parsers.** We decode untrusted PNG/JPEG/TIFF/BMP via Pillow.
  Keep Pillow pinned and updated; image decoders are a classic memory
  corruption surface.
- **Path handling.** Batch mode walks user-supplied directories. We
  refuse symlink traversal outside the input root and normalize all
  paths before write.
- **Plugin/adapter loading.** Third-party backends are opt-in and loaded
  by explicit module path from config, never auto-discovered from cwd.

## Out of scope

- Colorization quality. That's a model problem, not a security problem.
- Running with `--allow-remote-models` against a URL you don't trust.
  You asked for it.