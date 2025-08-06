import os
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

from PySide6 import QtWidgets, QtGui
from bang_py.ui_components.card_images import CardImageLoader, ACTION_ICON_MAP

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


@pytest.mark.parametrize("name", ["Bang!", "Draw Card", "Range 3"])
def test_compose_card_overlays_action_icon(name, qt_app):
    key = name.lower().replace("!", "").replace(" ", "_")
    assert key in ACTION_ICON_MAP
    loader = CardImageLoader()
    base = loader.compose_card("brown", rank="A", suit="Spades")
    with_icon = loader.compose_card("brown", rank="A", suit="Spades", name=name)
    assert with_icon.toImage() != base.toImage()


@pytest.mark.parametrize(
    "key",
    [
        "bang",
        "missed",
        "any_player",
        "all_players",
        "any_reachable_player",
        "draw_card",
        "discard_card",
        "discard_another_card",
        "gain_life",
        "range_1",
        "range_2",
        "range_3",
        "range_4",
        "range_5",
    ],
)
def test_action_icons_loaded(key, qt_app):
    loader = CardImageLoader()
    icon = loader.action_icons.get(key)
    assert icon is not None and not icon.isNull()


def test_compose_card_uses_cache(qt_app):
    loader = CardImageLoader()
    first = loader.compose_card("brown", rank="A", suit="Spades")
    second = loader.compose_card("brown", rank="A", suit="Spades")
    assert first is second


def test_clear_cache_invalidates(qt_app):
    loader = CardImageLoader()
    first = loader.compose_card("brown", rank="A", suit="Spades")
    loader.clear_cache()
    second = loader.compose_card("brown", rank="A", suit="Spades")
    assert first is not second


def test_reload_assets_clears_cache(qt_app):
    loader = CardImageLoader()
    first = loader.compose_card("brown", rank="A", suit="Spades")
    loader.reload_assets()
    second = loader.compose_card("brown", rank="A", suit="Spades")
    assert first is not second
