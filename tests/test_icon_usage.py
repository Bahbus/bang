from __future__ import annotations

"""Tests for ensuring all icons are referenced in the codebase."""

from pathlib import Path


# Icons that are intentionally present but unused.
# Document such icons here to prevent false positives.
KNOWN_UNUSED: set[str] = set()


def load_text_files(root: Path, icons_dir: Path) -> list[tuple[Path, str]]:
    """Return a list of (path, content) for text files in the repository.

    Icon files and the attribution file are skipped.
    """

    files: list[tuple[Path, str]] = []
    attribution = root / "bang_py" / "assets" / "ATTRIBUTION.md"
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.is_relative_to(icons_dir) or path == attribution:
            continue
        try:
            files.append((path, path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            continue
    return files


def test_all_icons_are_used() -> None:
    """Ensure that every icon file is referenced somewhere in the codebase."""

    repo_root = Path(__file__).resolve().parents[1]
    icons_dir = repo_root / "bang_py" / "assets" / "icons"
    text_files = load_text_files(repo_root, icons_dir)

    unused = []
    for icon in icons_dir.iterdir():
        if not icon.is_file():
            continue
        if icon.name in KNOWN_UNUSED:
            continue
        name = icon.name
        if not any(name in content for _, content in text_files):
            unused.append(name)

    assert not unused, f"Unused icons: {unused}. Remove them or add to KNOWN_UNUSED."
