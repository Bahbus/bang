from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.player import Player
from bang_py.cards.bang import BangCard
from bang_py.characters import BartCassidy


def test_drawing_and_playing():
    gm = GameManager(deck=Deck([BangCard(), BangCard()]))
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.draw_card(p1)
    assert len(p1.hand) == 1
    gm.play_card(p1, p1.hand[0], p2)
    assert len(gm.discard_pile) == 1
    assert p2.health == p2.max_health - 1


def test_bart_cassidy_draw_on_damage():
    gm = GameManager(deck=Deck([BangCard()]))
    p1 = Player("Bart", character=BartCassidy())
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.hand.append(BangCard())
    gm.play_card(p2, p2.hand[0], p1)
    assert len(p1.hand) == 1
