import pytest

pytest.importorskip("pytestqt", exc_type=ImportError)

from bang_py.network.validation import validate_player_name  # noqa: E402


def test_name_too_long_rejected() -> None:
    assert not validate_player_name("x" * 21)


def test_name_with_unprintable_rejected() -> None:
    assert not validate_player_name("bad\x00name")


def test_ui_invalid_name_shows_error(qt_app, monkeypatch) -> None:
    pytest.importorskip("cryptography")
    pytest.importorskip("PySide6", exc_type=ImportError)
    pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

    from PySide6 import QtWidgets
    from bang_py import ui as ui_module

    errors: dict[str, str] = {}

    def fake_critical(parent, title, text):
        errors["text"] = text

    monkeypatch.setattr(QtWidgets.QMessageBox, "critical", fake_critical)

    called: dict[str, bool] = {}

    def fake_start_host(self, port, max_players, certfile, keyfile):
        called["called"] = True

    monkeypatch.setattr(ui_module.BangUI, "_start_host", fake_start_host)

    ui = ui_module.BangUI()
    ui._host_menu("bad\x00name", "8765", "7", "", "")
    assert errors["text"] == "Please enter a valid name"
    assert "called" not in called
    ui.close()
