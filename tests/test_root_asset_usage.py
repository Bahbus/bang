from __future__ import annotations

"""Tests for ensuring root-level PNG assets are referenced in the codebase."""

from pathlib import Path


# Root-level PNG assets that are intentionally present but unused.
# Document such files here to prevent false positives.
KNOWN_UNUSED: set[str] = {"bullet.png", "table.png"}


def load_text_files(root: Path, assets_dir: Path) -> list[tuple[Path, str]]:
    """Return (path, content) pairs for text files outside the assets directory."""

    files: list[tuple[Path, str]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.is_relative_to(assets_dir):
            continue
        try:
            files.append((path, path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            continue
    return files


def test_all_root_png_assets_are_used() -> None:
    """Ensure that PNG files outside excluded folders are referenced."""

    repo_root = Path(__file__).resolve().parents[1]
    assets_dir = repo_root / "bang_py" / "assets"
    text_files = load_text_files(repo_root, assets_dir)

    excluded = {assets_dir / name for name in ("audio", "icons", "characters")}
    unused: list[str] = []

    for path in assets_dir.rglob("*.png"):
        if any(path.is_relative_to(folder) for folder in excluded):
            continue
        if path.name in KNOWN_UNUSED:
            continue
        if not any(path.name in content for _, content in text_files):
            unused.append(path.name)

    assert (
        not unused
    ), "Unused root PNG assets: {unused}. Remove them or add to KNOWN_UNUSED.".format(unused=unused)
