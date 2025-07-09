import json
from bang_py.player import Player, Role
from bang_py.network.server import _serialize_players


def test_serialize_players_json_roundtrip():
    players = [Player("Alice"), Player("Bob", role=Role.SHERIFF)]
    serialized = _serialize_players(players)
    json_str = json.dumps(serialized)
    loaded = json.loads(json_str)
    assert loaded == [
        {"name": "Alice", "health": players[0].health, "role": "OUTLAW"},
        {"name": "Bob", "health": players[1].health, "role": "SHERIFF"},
    ]

