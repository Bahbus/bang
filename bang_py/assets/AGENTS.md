# Asset Guidelines

Use this directory for game assets. Follow these rules:

## Naming
- File names must use lowercase and underscores (e.g. `bang_icon.webp`).
- Avoid spaces or special characters.

## Formats
- Images: `.png` or `.webp`.
- Audio: `.mp3`.

Do not add other formats without a compelling reason.

## Attribution
- Record the origin and license for every asset in `ATTRIBUTION.md` whenever assets change.

## Tests
- `tests/test_audio_usage.py`, `tests/test_icon_usage.py`, and
  `tests/test_root_asset_usage.py` check that assets referenced by the code
  exist and that unused files are avoided.
- After changing assets, run `uv run pre-commit run --files <file> [<file> ...]`
  and `uv run pytest tests/test_audio_usage.py tests/test_icon_usage.py
  tests/test_root_asset_usage.py`.
