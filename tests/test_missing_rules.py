from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard
from bang_py.cards.bang import BangCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.panic import PanicCard
from bang_py.cards.jail import JailCard


def test_bang_requires_range():
    gm = GameManager()
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    attacker.hand.append(BangCard())
    # default distance is 1 so attack succeeds
    gm.play_card(attacker, attacker.hand[0], target)
    assert target.health == target.max_health - 1
    target.health = target.max_health
    # give target Mustang to increase distance to 2
    from bang_py.cards.mustang import MustangCard

    MustangCard().play(target)
    attacker.hand.append(BangCard())
    gm.play_card(attacker, attacker.hand[-1], target)
    # out of range, no damage and card still in hand
    assert target.health == target.max_health
    assert len(attacker.hand) == 1


def test_panic_requires_range_one():
    gm = GameManager()
    p1 = Player("One")
    p2 = Player("Two")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.hand.append(BangCard())
    p1.hand.append(PanicCard())
    # Increase distance to 2
    from bang_py.cards.mustang import MustangCard

    MustangCard().play(p2)
    gm.play_card(p1, p1.hand[0], p2)
    assert len(p2.hand) == 1
    assert len(p1.hand) == 1


def test_beer_no_effect_with_two_players():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.health -= 1
    BeerCard().play(p1)
    assert p1.health == p1.max_health - 1


def test_jail_cannot_target_sheriff():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    jail = JailCard()
    outlaw.hand.append(jail)
    gm.play_card(outlaw, jail, sheriff)
    assert "Jail" not in sheriff.equipment
    assert len(outlaw.hand) == 1
