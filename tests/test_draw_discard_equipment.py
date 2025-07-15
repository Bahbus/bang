from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.player import Player
from bang_py.cards.bang import BangCard
from bang_py.cards.scope import ScopeCard
from bang_py.cards.mustang import MustangCard
from bang_py.cards.iron_plate import IronPlateCard
from bang_py.cards.cat_balou import CatBalouCard
from bang_py.characters.black_jack import BlackJack
from bang_py.characters.sid_ketchum import SidKetchum


def test_draw_phase_black_jack_extra_card():
    deck = Deck([])
    deck.cards = [BangCard(), BangCard(suit="Hearts"), BangCard()]
    gm = GameManager(deck=deck)
    p = Player("BJ", character=BlackJack())
    gm.add_player(p)
    gm.draw_phase(p)
    # Black Jack should draw all three cards since second is Hearts
    assert len(p.hand) == 3


def test_discard_phase_limits_hand_to_health():
    gm = GameManager(deck=Deck([]))
    p = Player("A")
    gm.add_player(p)
    p.hand.extend([BangCard() for _ in range(4)])
    p.health = 2
    gm.discard_phase(p)
    assert len(p.hand) == 2


def test_equipment_modifies_range_and_distance():
    attacker = Player("Att")
    target = Player("Tgt")
    ScopeCard().play(attacker)
    MustangCard().play(target)
    assert attacker.attack_range == 2
    assert attacker.distance_to(target) == 1


def test_sid_ketchum_discard_two_to_heal():
    gm = GameManager(deck=Deck([]))
    sid = Player("Sid", character=SidKetchum())
    gm.add_player(sid)
    sid.health = sid.max_health - 1
    sid.hand.extend([BangCard(), BangCard()])
    sid.character.use_ability(gm, sid, [0, 1])
    assert sid.health == sid.max_health
    assert len(sid.hand) == 0


def test_iron_plate_is_missed():
    target = Player("T")
    IronPlateCard().play(target)
    assert target.metadata.dodged is True
