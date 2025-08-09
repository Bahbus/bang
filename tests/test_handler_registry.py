from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.player import Player
from bang_py.cards import BangCard
from bang_py.cards.pony_express import PonyExpressCard
from bang_py.card_handlers import (
    CardHandlersMixin,
    register_handler_groups,
)


def test_register_specific_handler_groups():
    assert hasattr(CardHandlersMixin, "_dispatch_play")
    assert hasattr(CardHandlersMixin, "_play_bang_card")

    deck = Deck([BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    gm._card_handlers = {}
    register_handler_groups(gm, ["basic"])
    p1 = Player("A")
    gm.add_player(p1)
    card = PonyExpressCard()
    p1.hand.append(card)
    gm.play_card(p1, card)
    assert len(p1.hand) == 0

    gm._card_handlers = {}
    p1.hand.append(PonyExpressCard())
    register_handler_groups(gm, ["basic", "green"])
    gm.play_card(p1, p1.hand[0])
    assert len(p1.hand) == 3
