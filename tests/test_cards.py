from bang_py.cards.bang import BangCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.missed import MissedCard
from bang_py.player import Player


def test_bang_card_damages_target():
    target = Player("Target")
    BangCard().play(target)
    assert target.health == target.max_health - 1


def test_beer_card_heals_target():
    target = Player("Target")
    target.health = target.max_health - 1
    BeerCard().play(target)
    assert target.health == target.max_health
    BeerCard().play(target)
    assert target.health == target.max_health


def test_missed_card_sets_dodged_metadata():
    target = Player("Target")
    MissedCard().play(target)
    assert target.metadata.get("dodged") is True
