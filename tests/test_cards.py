from bang_py.cards.bang import BangCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.missed import MissedCard
from bang_py.cards.barrel import BarrelCard
from bang_py.cards.schofield import SchofieldCard
from bang_py.cards.volcanic import VolcanicCard
from bang_py.cards.scope import ScopeCard
from bang_py.cards.mustang import MustangCard
from bang_py.cards.jail import JailCard
from bang_py.cards.dynamite import DynamiteCard
from bang_py.deck import Deck
from bang_py.deck_factory import create_standard_deck
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


def test_equipment_replaces_same_name():
    target = Player("Target")
    BarrelCard().play(target)
    assert "Barrel" in target.equipment
    # Play another barrel, should replace existing (no duplicate entries)
    BarrelCard().play(target)
    assert list(target.equipment.keys()).count("Barrel") == 1


def test_gun_slot_only_one_equipped():
    target = Player("Target")
    SchofieldCard().play(target)
    assert target.equipment["Gun"].card_name == "Schofield"
    VolcanicCard().play(target)
    assert target.equipment["Gun"].card_name == "Volcanic"


def test_scope_increases_attack_range():
    player = Player("Shooter")
    assert player.attack_range == 1
    ScopeCard().play(player)
    assert player.attack_range == 2
    SchofieldCard().play(player)
    assert player.attack_range == 3  # gun range 2 + scope 1


def test_mustang_increases_distance():
    p1 = Player("One")
    p2 = Player("Two")
    assert p1.distance_to(p2) == 1
    MustangCard().play(p2)
    assert p1.distance_to(p2) == 2
    ScopeCard().play(p1)
    assert p1.distance_to(p2) == 1


def test_barrel_dodges_bang_on_heart():
    target = Player("Target")
    BarrelCard().play(target)
    deck = create_standard_deck()
    deck.cards.append(BeerCard(suit="Hearts"))
    BangCard().play(target, deck)
    assert target.health == target.max_health
    assert target.metadata.get("dodged") is True


def test_barrel_fails_on_non_heart():
    target = Player("Target")
    BarrelCard().play(target)
    deck = create_standard_deck()
    deck.cards.append(BeerCard(suit="Clubs"))
    BangCard().play(target, deck)
    assert target.health == target.max_health - 1


def test_jail_skip_turn():
    player = Player("Prisoner")
    jail = JailCard()
    jail.play(player)
    deck = create_standard_deck()
    deck.cards.append(BangCard(suit="Clubs"))
    skipped = jail.check_turn(player, deck)
    assert skipped is True
    assert "Jail" not in player.equipment


def test_jail_freed_on_heart():
    player = Player("Prisoner")
    jail = JailCard()
    jail.play(player)
    deck = create_standard_deck()
    deck.cards.append(BangCard(suit="Hearts"))
    skipped = jail.check_turn(player, deck)
    assert skipped is False
    assert "Jail" not in player.equipment


def test_dynamite_explodes():
    p1 = Player("One")
    p2 = Player("Two")
    dyn = DynamiteCard()
    dyn.play(p1)
    deck = create_standard_deck()
    deck.cards.append(BangCard(suit="Spades", rank=5))
    exploded = dyn.check_dynamite(p1, p2, deck)
    assert exploded is True
    assert p1.health == p1.max_health - 3
    assert "Dynamite" not in p1.equipment


def test_dynamite_passes():
    p1 = Player("One")
    p2 = Player("Two")
    dyn = DynamiteCard()
    dyn.play(p1)
    deck = create_standard_deck()
    deck.cards.append(BangCard(suit="Hearts", rank=1))
    exploded = dyn.check_dynamite(p1, p2, deck)
    assert exploded is False
    assert "Dynamite" not in p1.equipment
    assert "Dynamite" in p2.equipment
