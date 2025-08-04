import os
import pytest

pytest.importorskip("PySide6", reason="PySide6 not installed; skipping GUI tests")

from PySide6 import QtWidgets
from bang_py.ui_components.card_images import load_sound


def test_load_sound_mp3():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QtWidgets.QApplication.instance()
    created = app is None
    if created:
        app = QtWidgets.QApplication([])
    sound = load_sound("ui_click")
    if created:
        app.quit()
    if sound is None:
        pytest.skip("QtMultimedia not available")
    assert hasattr(sound, "play")
