import os

import pytest

from bang_py.ui import BangUI
from PySide6 import QtWidgets


@pytest.fixture
def qt_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QtWidgets.QApplication.instance()
    created = app is None
    if created:
        app = QtWidgets.QApplication([])
    yield app
    if created:
        app.quit()

def test_bang_ui_creation(qt_app):
    ui = BangUI()
    assert ui.windowTitle() == "Bang!"
    ui.close()
