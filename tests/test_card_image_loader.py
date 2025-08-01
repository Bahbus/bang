import os
import pytest

pytest.importorskip("PySide6", reason="PySide6 not installed; skipping GUI tests")

from PySide6 import QtWidgets, QtGui


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


@pytest.mark.parametrize(
    "card_type,kwargs",
    [
        ("brown", {"rank": "A", "suit": "Spades"}),
        ("blue", {"rank": 10, "suit": "Hearts"}),
        ("green", {"rank": "K", "suit": "Diamonds"}),
        ("character", {}),
        ("role", {}),
        ("event", {"card_set": "fistful_of_cards"}),
    ],
)
def test_compose_card_returns_pixmap(card_type, kwargs, qt_app):
    from bang_py.ui_components.card_images import CardImageLoader

    loader = CardImageLoader()
    pix = loader.compose_card(card_type, **kwargs)
    assert isinstance(pix, QtGui.QPixmap)
    assert not pix.isNull()


@pytest.mark.parametrize("name", ["other", "role", "character"])
def test_get_card_back_returns_pixmap(name, qt_app):
    from bang_py.ui_components.card_images import CardImageLoader

    loader = CardImageLoader()
    pix = loader.get_card_back(name)
    assert isinstance(pix, QtGui.QPixmap)
    assert not pix.isNull()
