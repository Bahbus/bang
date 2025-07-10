from bang_py.player import Player, Role
from bang_py.characters import Character

class BonusLife(Character):
    max_health_modifier = 1


def test_bonus_life_character_increases_max_health():
    p = Player("Hero", role=Role.OUTLAW, character=BonusLife())
    assert p.max_health == 5
    assert p.health == 5
    sheriff = Player("Sheriff", role=Role.SHERIFF, character=BonusLife())
    assert sheriff.max_health == 6
    assert sheriff.health == 6

