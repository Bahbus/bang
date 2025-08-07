from __future__ import annotations

"""Tests for ensuring all character images correspond to character code."""

from pathlib import Path


# Character images that are intentionally present but unused.
# Document such images here to prevent false positives.
KNOWN_UNUSED: set[str] = set()


def load_character_texts(characters_dir: Path) -> list[str]:
    """Return the text content of all character modules."""
    texts: list[str] = []
    for path in characters_dir.glob("*.py"):
        try:
            texts.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    return texts


def test_all_character_images_are_used() -> None:
    """Ensure that every character image is referenced in the codebase."""

    repo_root = Path(__file__).resolve().parents[1]
    image_dir = repo_root / "bang_py" / "assets" / "characters"
    characters_dir = repo_root / "bang_py" / "characters"
    texts = load_character_texts(characters_dir)

    unused = []
    for image in image_dir.glob("*.webp"):
        name = image.stem
        if name in KNOWN_UNUSED:
            continue
        if not any(name in text for text in texts):
            unused.append(f"{name}.webp")

    assert not unused, f"Unused character images: {unused}. Remove them or add to KNOWN_UNUSED."
