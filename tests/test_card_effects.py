import random

from bang_py.cards.bang import BangCard
from bang_py.cards.barrel import BarrelCard
from bang_py.cards.missed import MissedCard
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
