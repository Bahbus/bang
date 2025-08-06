import pytest

pytest.importorskip(
    "PySide6", reason="PySide6 not installed; skipping GUI tests", exc_type=ImportError
)
pytest.importorskip(
    "PySide6.QtWidgets",
    reason="QtWidgets unavailable; skipping GUI tests",
    exc_type=ImportError,
)
pytest.importorskip(
    "PySide6.QtGui",
    reason="QtGui unavailable; skipping GUI tests",
    exc_type=ImportError,
)
from PySide6 import QtGui
from bang_py.helpers import RankSuitIconLoader


def test_loader_returns_pixmap(qt_app):
    loader = RankSuitIconLoader()
    pix = loader.get_pixmap("A", "Hearts")
    assert isinstance(pix, QtGui.QPixmap)
    assert not pix.isNull()
