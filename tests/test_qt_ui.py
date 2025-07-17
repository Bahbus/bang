import os
import json

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


def test_broadcast_state_updates_ui(qt_app):
    ui = BangUI()
    ui._build_game_view()
    state = {
        "players": [
            {"name": "Alice", "health": 4, "role": "Sheriff", "equipment": []},
            {"name": "Bob", "health": 3, "role": "Outlaw", "equipment": []},
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
