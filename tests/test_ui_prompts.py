import pytest

# mypy: ignore-errors

pytest.importorskip(
    "PySide6", reason="PySide6 not installed; skipping GUI tests", exc_type=ImportError
)
pytest.importorskip(
    "PySide6.QtCore",
    reason="QtCore unavailable; skipping GUI tests",
    exc_type=ImportError,
)
pytest.importorskip(
    "PySide6.QtWidgets",
    reason="QtWidgets unavailable; skipping GUI tests",
    exc_type=ImportError,
)
pytest.importorskip(
    "PySide6.QtQml",
    reason="QtQml unavailable; skipping GUI tests",
    exc_type=ImportError,
)

from PySide6 import QtQml  # noqa: E402


def _load_component(name: str) -> QtQml.QQmlComponent:
    from importlib import resources

    qml_dir = resources.files("bang_py.ui") / "qml"
    with resources.as_file(qml_dir / name) as path:
        engine = QtQml.QQmlEngine()
        comp = QtQml.QQmlComponent(engine, str(path))
        comp._engine = engine  # prevent engine from being garbage-collected
        return comp


def test_option_prompt_emits_index(qt_app):
    comp = _load_component("OptionPrompt.qml")
    dialog = comp.create()
    dialog.setProperty("options", ["a", "b"])
    captured = {}

    def _got(i: int) -> None:
        captured["index"] = i

    dialog.acceptedIndex.connect(_got)
    dialog.setProperty("selectedIndex", 1)
    dialog.accept()
    qt_app.processEvents()
    assert captured["index"] == 1
    dialog.deleteLater()


def test_confirm_prompt_accepts(qt_app):
    comp = _load_component("ConfirmPrompt.qml")
    dialog = comp.create()
    result = {"ok": False}
    dialog.accepted.connect(lambda: result.__setitem__("ok", True))
    dialog.accept()
    qt_app.processEvents()
    assert result["ok"]
    dialog.deleteLater()


def test_show_prompt_general_store_sends_action(qt_app, monkeypatch):
    from bang_py.ui import BangUI

    ui = BangUI()
    called = {}

    def fake_send(payload: dict) -> None:
        called["payload"] = payload

    monkeypatch.setattr(ui, "_send_action", fake_send)
    monkeypatch.setattr(ui, "_option_prompt", lambda title, opts, cb: cb(1))
    ui._show_prompt("general_store", {"cards": ["Bang", "Missed"]})
    assert called["payload"] == {"action": "general_store_pick", "index": 1}
    ui.close()
