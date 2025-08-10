import random

from bang_py.cards.bang import BangCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.missed import MissedCard
from bang_py.deck import Deck
from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.characters.sid_ketchum import SidKetchum
from bang_py.characters.uncle_will import UncleWill


def test_sid_ketchum_heal_ability() -> None:
    random.seed(0)
    gm = GameManager()
    sid = Player("Sid", character=SidKetchum())
    gm.add_player(sid)
    assert isinstance(sid.character, SidKetchum)
    sid.hand.extend([BangCard(), BeerCard()])
    sid.health -= 1
    assert sid.character.use_ability(gm, sid, [0, 1])
    assert sid.health == sid.max_health
    assert not sid.hand


def test_general_store_pick_sequence() -> None:
    random.seed(0)
    deck = Deck([])
    deck.push_top(MissedCard())
    deck.push_top(BeerCard())
    deck.push_top(BangCard())
    gm = GameManager(deck=deck)
    p1, p2, p3 = Player("A"), Player("B"), Player("C")
    for p in (p1, p2, p3):
        gm.add_player(p)
    revealed = gm.start_general_store(p1)
    assert revealed == ["Bang!", "Beer", "Missed!"]
    assert not gm.general_store_pick(p2, 0)
    assert gm.general_store_pick(p1, 1)
    assert gm.general_store_pick(p2, 0)
    assert gm.general_store_pick(p3, 0)
    assert gm.general_store_cards is None
    assert p1.hand[0].card_name == "Beer"
    assert p2.hand[0].card_name == "Bang!"
    assert p3.hand[0].card_name == "Missed!"


def test_uncle_will_general_store_ability() -> None:
    random.seed(0)
    deck = Deck([])
    deck.push_top(BeerCard())
    deck.push_top(BangCard())
    gm = GameManager(deck=deck)
    will = Player("Will", character=UncleWill())
    other = Player("Other")
    for p in (will, other):
        gm.add_player(p)
    will.hand.append(MissedCard())
    assert gm.uncle_will_ability(will, will.hand[0])
    assert will.metadata.uncle_used
    assert will.hand[0].card_name == "Bang!"
    assert other.hand[0].card_name == "Beer"
    assert gm.discard_pile[-1].card_name == "Missed!"
