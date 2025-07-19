import os
import pytest

pytest.importorskip("PySide6")
from PySide6 import QtWidgets, QtGui
from bang_py.helpers import RankSuitIconLoader


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


def test_loader_returns_pixmap(qt_app):
    loader = RankSuitIconLoader()
    pix = loader.get_pixmap("A", "Hearts")
    assert isinstance(pix, QtGui.QPixmap)
    assert not pix.isNull()
