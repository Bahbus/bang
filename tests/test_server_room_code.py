import secrets
import pytest

pytest.importorskip("cryptography")

from bang_py.network.server import BangServer


def test_default_room_code_format(monkeypatch) -> None:
    monkeypatch.setattr(secrets, "token_hex", lambda n=3: "abc123")
    server = BangServer()
    assert server.room_code == "abc123"
    assert server.room_code.isalnum()
    assert len(server.room_code) == 6


def test_default_room_code_unique(monkeypatch) -> None:
    values = iter(["aaaaaa", "bbbbbb"])
    monkeypatch.setattr(secrets, "token_hex", lambda n=3: next(values))
    server1 = BangServer()
    server2 = BangServer()
    assert server1.room_code != server2.room_code
