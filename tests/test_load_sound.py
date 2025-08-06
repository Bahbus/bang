import os
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

from PySide6 import QtWidgets  # noqa: E402
from bang_py.ui.components.card_images import clear_sound_cache, load_sound  # noqa: E402


def _prepare_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    audio_path = (
        Path(__file__).resolve().parents[1] / "bang_py" / "assets" / "audio" / "ui_click.mp3"
    )
    if not audio_path.exists():
        pytest.skip("ui_click.mp3 not generated")
    app = QtWidgets.QApplication.instance()
    created = app is None
    if created:
        app = QtWidgets.QApplication([])
    return app, created


def test_load_sound_mp3():
    app, created = _prepare_app()
    clear_sound_cache()
    sound = load_sound("ui_click")
    if created:
        app.quit()
    if sound is None:
        pytest.skip("QtMultimedia not available")
    assert hasattr(sound, "play")
    clear_sound_cache()


def test_load_sound_cache():
    app, created = _prepare_app()
    clear_sound_cache()
    sound1 = load_sound("ui_click")
    sound2 = load_sound("ui_click")
    if sound1 is None:
        if created:
            app.quit()
        pytest.skip("QtMultimedia not available")
    assert sound1 is sound2
    clear_sound_cache()
    sound3 = load_sound("ui_click")
    if created:
        app.quit()
    if sound3 is None:
        pytest.skip("QtMultimedia not available")
    assert sound1 is not sound3
    clear_sound_cache()
