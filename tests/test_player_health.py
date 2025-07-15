from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard, OutlawRoleCard
from bang_py.characters.base import BaseCharacter


class BonusLife(BaseCharacter):
    def ability(self, *_: object, **__: object) -> bool:
        return False
    starting_health = 5


def test_bonus_life_character_increases_max_health():
    p = Player("Hero", role=OutlawRoleCard(), character=BonusLife())
    assert p.max_health == 5
    assert p.health == 5
    sheriff = Player("Sheriff", role=SheriffRoleCard(), character=BonusLife())
    assert sheriff.max_health == 6
    assert sheriff.health == 6
