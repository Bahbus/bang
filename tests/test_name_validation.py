import pytest

pytest.importorskip("cryptography")
pytest.importorskip("websockets")

from bang_py.network.server import validate_player_name


def test_name_too_long_rejected() -> None:
    assert not validate_player_name("x" * 21)


def test_name_with_unprintable_rejected() -> None:
    assert not validate_player_name("bad\x00name")

