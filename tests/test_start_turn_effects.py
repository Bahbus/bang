from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.cards.bang import BangCard
from bang_py.cards.jail import JailCard
from bang_py.cards.dynamite import DynamiteCard
from bang_py.player import Player


def test_jail_auto_skip_turn():
    deck = Deck([])
    deck.extend_top([BangCard(), BangCard(), BangCard(suit="Clubs")])
    gm = GameManager(deck=deck)
    p1 = Player("Jailbird")
    p2 = Player("Other")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    JailCard().play(p1)
    gm._begin_turn()
    assert gm.current_turn == 1
    assert "Jail" not in p1.equipment
    assert len(gm.discard_pile) == 2
    assert len(p1.hand) == 0


def test_dynamite_explodes_on_turn_start():
    deck = Deck([])
    deck.extend_top([BangCard(), BangCard(), BangCard(suit="Spades", rank=5)])
    gm = GameManager(deck=deck)
    p1 = Player("One")
    p2 = Player("Two")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    DynamiteCard().play(p1)
    gm._begin_turn()
    assert p1.health == p1.max_health - 3
    assert "Dynamite" not in p1.equipment
    assert len(gm.discard_pile) == 2


def test_dynamite_passes_to_next_player():
    deck = Deck([])
    deck.extend_top([BangCard(), BangCard(), BangCard(suit="Hearts", rank=1)])
    gm = GameManager(deck=deck)
    p1 = Player("One")
    p2 = Player("Two")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    DynamiteCard().play(p1)
    gm._begin_turn()
    assert "Dynamite" not in p1.equipment
    assert "Dynamite" in p2.equipment
    assert len(gm.discard_pile) == 1
