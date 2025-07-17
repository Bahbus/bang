import json
from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard, OutlawRoleCard
from bang_py.network.server import _serialize_players


def test_serialize_players_json_roundtrip():
    players = [Player("Alice", role=OutlawRoleCard()), Player("Bob", role=SheriffRoleCard())]
    assert players[0].max_health == 4
    assert players[1].max_health == 5
    serialized = _serialize_players(players)
    json_str = json.dumps(serialized)
    loaded = json.loads(json_str)
    assert loaded == [
        {
            "name": "Alice",
            "health": players[0].health,
            "role": "Outlaw",
            "equipment": [],
        },
        {
            "name": "Bob",
            "health": players[1].health,
            "role": "Sheriff",
            "equipment": [],
        },
    ]


def test_serialize_players_with_health_changes():
    sheriff = Player("Bill", role=SheriffRoleCard())
    sheriff.health = 3
    data = _serialize_players([sheriff])
    assert data == [
        {
            "name": "Bill",
            "health": 3,
            "role": "Sheriff",
            "equipment": [],
        }
    ]
