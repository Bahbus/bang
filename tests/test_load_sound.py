from pathlib import Path

import pytest

pytest.importorskip(
    "PySide6", reason="PySide6 not installed; skipping GUI tests", exc_type=ImportError
)
pytest.importorskip(
    "PySide6.QtWidgets",
    reason="QtWidgets unavailable; skipping GUI tests",
    exc_type=ImportError,
)

from bang_py.ui.components.card_images import clear_sound_cache, load_sound  # noqa: E402

AUDIO_PATH = Path(__file__).resolve().parents[1] / "bang_py" / "assets" / "audio" / "ui_click.mp3"
if not AUDIO_PATH.exists():  # pragma: no cover - asset generation handled elsewhere
    pytest.skip("ui_click.mp3 not generated", allow_module_level=True)


def test_load_sound_mp3(qt_app):
    clear_sound_cache()
    sound = load_sound("ui_click")
    if sound is None:
        pytest.skip("QtMultimedia not available")
    assert hasattr(sound, "play")
    clear_sound_cache()


def test_load_sound_cache(qt_app):
    clear_sound_cache()
    sound1 = load_sound("ui_click")
    sound2 = load_sound("ui_click")
    if sound1 is None:
        pytest.skip("QtMultimedia not available")
    assert sound1 is sound2
    clear_sound_cache()
    sound3 = load_sound("ui_click")
    if sound3 is None:
        pytest.skip("QtMultimedia not available")
    assert sound1 is not sound3
    clear_sound_cache()
