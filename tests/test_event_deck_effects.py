import random
from bang_py.event_decks import EventCard, _thirst, _fistful
from bang_py.game_manager import GameManager
from bang_py.player import Player, Role
from bang_py.cards import BangCard


def test_thirst_event_draw_one():
    gm = GameManager()
    gm.event_deck = [EventCard("Thirst", _thirst, "")]
    p = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(p)
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 1


def test_fistful_event_damage_by_hand():
    gm = GameManager()
    p = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(p)
    p.hand = [BangCard(), BangCard()]
    gm.event_deck = [EventCard("A Fistful of Cards", _fistful, "")]
    gm.turn_order = [0]
    gm.current_turn = 0
    gm._begin_turn()
    assert p.health == p.max_health - 2
