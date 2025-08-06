import json

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
    "PySide6.QtCore",
    reason="QtCore unavailable; skipping GUI tests",
    exc_type=ImportError,
)
pytest.importorskip(
    "PySide6.QtMultimedia",
    reason="QtMultimedia unavailable; skipping GUI tests",
    exc_type=ImportError,
)

from PySide6 import QtWidgets  # noqa: E402


def test_bang_ui_creation(qt_app):
    from bang_py.ui import BangUI

    ui = BangUI()
    ui.show()
    assert ui.view.title() == "Bang!"
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
                "character": "Lucky Duke",
            },
            {
                "name": "Bob",
                "health": 3,
                "role": "Outlaw",
                "equipment": [],
                "character": "Jesse Jones",
            },
        ],
        "hand": ["Bang", "Missed"],
        "character": "Test",
        "event": "",
    }
    ui._append_message(json.dumps(state))
    root = ui.game_root
    assert root is not None
    players = root.property("players")
    assert players[0]["portrait"] == "../assets/characters/lucky_duke.webp"
    assert players[1]["portrait"] == "../assets/characters/jesse_jones.webp"
    hand_prop = root.property("hand")
    assert isinstance(hand_prop, list)
    assert len(hand_prop) == 2
    ui.close()


def test_qml_board_signals(qt_app):
    from bang_py.ui import BangUI

    ui = BangUI()
    ui._build_game_view()
    root = ui.game_root
    triggered = {}

    def _draw():
        triggered["draw"] = True

    if root is not None:
        root.drawCard.connect(_draw)
        root.drawCard.emit()
    assert "draw" in triggered
    ui.close()


def test_dark_theme_from_env(qt_app, monkeypatch):
    monkeypatch.setenv("BANG_THEME", "dark")
    from bang_py.ui import BangUI

    ui = BangUI()
    assert ui.root.property("theme") == "dark"
    ui.close()


def test_join_menu_invalid_token_shows_error(qt_app, monkeypatch):
    from bang_py import ui as ui_module

    error_msg = {}

    def fake_critical(parent, title, text):
        error_msg["text"] = text

    monkeypatch.setattr(QtWidgets.QMessageBox, "critical", fake_critical)

    called = {}

    def fake_start_join(self, addr, port, code, cafile=None):
        called["called"] = True

    monkeypatch.setattr(ui_module.BangUI, "_start_join", fake_start_join)

    ui = ui_module.BangUI()
    ui._join_menu("Alice", "", "0", "invalid", "")
    assert error_msg["text"] == "Invalid token"
    assert "called" not in called
    ui.close()
