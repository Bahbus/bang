import os
import json

import pytest

pytest.importorskip("PySide6")

from PySide6 import QtWidgets, QtCore, QtGui  # noqa: E402


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
    from bang_py.ui import BangUI

    ui = BangUI()
    assert ui.windowTitle() == "Bang!"
    ui.close()


def test_broadcast_state_updates_ui(qt_app):
    from bang_py.ui import BangUI

    ui = BangUI()
    ui._build_game_view()
    state = {
        "players": [
            {
                "name": "Alice",
                "health": 4,
                "role": "Sheriff",
                "equipment": [],
                "character": "",
            },
            {
                "name": "Bob",
                "health": 3,
                "role": "Outlaw",
                "equipment": [],
                "character": "",
            },
        ],
        "hand": ["Bang", "Missed"],
        "character": "Test",
        "event": "",
    }
    ui._append_message(json.dumps(state))
    assert ui.player_list.count() == 2
    assert ui.board.players == state["players"]
    assert ui.hand_layout.count() == 2
    ui.close()


def test_gameboard_uses_available_geometry(qt_app, monkeypatch):
    from bang_py.ui_components.game_view import GameBoard
    rect = QtCore.QRect(0, 0, 1234, 987)

    class DummyScreen:
        def availableGeometry(self):
            return rect

    monkeypatch.setattr(QtGui.QGuiApplication, "primaryScreen", lambda: DummyScreen())
    board = GameBoard()
    assert board.max_width == rect.width()
    assert board.max_height == rect.height()
    board.close()


def test_gameboard_bullets(qt_app):
    from bang_py.ui_components.game_view import GameBoard

    board = GameBoard()
    assert not board.bullet_pixmap.isNull()

    players = [
        {"name": "Alice", "health": 3},
        {"name": "Bob", "health": 2},
    ]
    board.update_players(players)

    bullet_size = board.bullet_pixmap.size()
    bullet_items = [
        item
        for item in board._scene.items()
        if isinstance(item, QtWidgets.QGraphicsPixmapItem)
        and item.pixmap().size() == bullet_size
    ]
    assert len(bullet_items) == sum(p["health"] for p in players)

    tooltips = [
        item.toolTip()
        for item in board._scene.items()
        if isinstance(item, QtWidgets.QGraphicsTextItem)
    ]
    assert "Health: 3" in tooltips
    assert "Health: 2" in tooltips
    board.close()


def test_gameboard_table_pixmap(qt_app):
    from bang_py.ui_components.game_view import GameBoard

    board = GameBoard()
    assert not board.table_pixmap.isNull()
    board.close()


def test_dark_theme_from_env(qt_app, monkeypatch):
    monkeypatch.setenv("BANG_THEME", "dark")
    from bang_py.ui import BangUI

    ui = BangUI()
    assert "#2b2b2b" in ui.styleSheet()
    ui.close()
