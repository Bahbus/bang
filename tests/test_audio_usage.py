from __future__ import annotations

"""Tests for ensuring all audio files are referenced in the codebase."""

from pathlib import Path


# Audio files that are intentionally present but unused.
# Document such files here to prevent false positives.
KNOWN_UNUSED: set[str] = {".gitkeep"}


def load_text_files(root: Path, audio_dir: Path) -> list[tuple[Path, str]]:
    """Return a list of (path, content) for text files in the repository.

    Audio files and the attribution file are skipped.
    """

    files: list[tuple[Path, str]] = []
    attribution = root / "bang_py" / "assets" / "ATTRIBUTION.md"
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.is_relative_to(audio_dir) or path == attribution:
            continue
        try:
            files.append((path, path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            continue
    return files


def test_all_audio_files_are_used() -> None:
    """Ensure that every audio file is referenced somewhere in the codebase."""

    repo_root = Path(__file__).resolve().parents[1]
    audio_dir = repo_root / "bang_py" / "assets" / "audio"
    text_files = load_text_files(repo_root, audio_dir)

    unused = []
    for audio in audio_dir.iterdir():
        if not audio.is_file():
            continue
        if audio.name in KNOWN_UNUSED:
            continue
        name = audio.name
        if not any(name in content for _, content in text_files):
            unused.append(name)

    assert not unused, f"Unused audio files: {unused}. Remove them or add to KNOWN_UNUSED."
