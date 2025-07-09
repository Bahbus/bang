import pytest

from bang_py.game_manager import GameManager
from bang_py.player import Player


def test_start_game_initializes_turn_order_and_calls_listener():
    gm = GameManager()
    p1 = Player("Alice")
    p2 = Player("Bob")
    gm.add_player(p1)
    gm.add_player(p2)
    started_players = []
    gm.turn_started_listeners.append(lambda player: started_players.append(player))

    gm.start_game()

    assert gm.turn_order == [0, 1]
    assert gm.current_turn == 0
    assert started_players == [p1]
