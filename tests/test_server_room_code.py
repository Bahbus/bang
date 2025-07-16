import secrets
from bang_py.network.server import BangServer


def test_default_room_code_format(monkeypatch) -> None:
    monkeypatch.setattr(secrets, "randbelow", lambda _: 123)
    server = BangServer()
    assert server.room_code == "1123"
    assert server.room_code.isdigit()
    assert len(server.room_code) == 4


def test_default_room_code_unique(monkeypatch) -> None:
    values = iter([1, 2])
    monkeypatch.setattr(secrets, "randbelow", lambda _: next(values))
    server1 = BangServer()
    server2 = BangServer()
    assert server1.room_code != server2.room_code

