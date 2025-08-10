import random

from bang_py.cards.bang import BangCard
from bang_py.cards.barrel import BarrelCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.general_store import GeneralStoreCard
from bang_py.cards.missed import MissedCard
from bang_py.deck import Deck
from bang_py.game_manager import GameManager
from bang_py.player import Player


def test_ricochet_shoot_discards_equipment() -> None:
    random.seed(0)
    gm = GameManager()
    shooter = Player("Shooter")
    target = Player("Target")
    gm.add_player(shooter)
    gm.add_player(target)
    gm.event_flags["ricochet"] = True
    shooter.hand.append(BangCard())
    barrel = BarrelCard()
    barrel.play(target)
    assert gm.ricochet_shoot(shooter, target, "Barrel")
    assert "Barrel" not in target.equipment
    assert any(c.card_name == "Barrel" for c in gm.discard_pile)
    assert all(not isinstance(c, BangCard) for c in shooter.hand)


def test_ricochet_shoot_blocked_by_miss() -> None:
    random.seed(0)
    gm = GameManager()
    shooter = Player("Shooter")
    target = Player("Target")
    gm.add_player(shooter)
    gm.add_player(target)
    gm.event_flags["ricochet"] = True
    shooter.hand.append(BangCard())
    barrel = BarrelCard()
    barrel.play(target)
    target.hand.append(MissedCard())
    assert not gm.ricochet_shoot(shooter, target, "Barrel")
    assert "Barrel" in target.equipment
    assert any(isinstance(c, MissedCard) for c in gm.discard_pile)
    assert all(not isinstance(c, BangCard) for c in shooter.hand)


def test_general_store_card_allows_picks() -> None:
    random.seed(0)
    deck = Deck([])
    deck.push_top(MissedCard())
    deck.push_top(BeerCard())
    deck.push_top(BangCard())
    gm = GameManager(deck=deck)
    p1, p2, p3 = Player("A"), Player("B"), Player("C")
    for p in (p1, p2, p3):
        gm.add_player(p)
    card = GeneralStoreCard()
    card.play(None, player=p1, game=gm, choices=[1, 1, 0])
    assert gm.general_store_cards is None
    assert p1.hand[0].card_name == "Beer"
    assert p2.hand[0].card_name == "Missed!"
    assert p3.hand[0].card_name == "Bang!"


def test_bang_triggers_damage_listeners() -> None:
    random.seed(0)
    gm = GameManager()
    shooter = Player("Shooter")
    target = Player("Target")
    gm.add_player(shooter)
    gm.add_player(target)
    events: list[tuple[Player, Player | None]] = []
    gm.player_damaged_listeners.append(lambda p, s: events.append((p, s)))
    shooter.hand.append(BangCard())
    gm.play_card(shooter, shooter.hand[0], target)
    assert events == [(target, shooter)]
    assert target.health == target.max_health - 1
