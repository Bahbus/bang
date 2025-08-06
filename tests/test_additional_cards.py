from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.player import Player
from bang_py.cards import (
    StagecoachCard,
    WellsFargoCard,
    CatBalouCard,
    PanicCard,
    IndiansCard,
    DuelCard,
    GeneralStoreCard,
    SaloonCard,
    GatlingCard,
    BeerCard,
    BangCard,
)
from collections import deque


def test_stagecoach_draws_two_cards():
    deck = Deck([BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p = Player("A")
    gm.add_player(p)
    StagecoachCard().play(p, game=gm)
    assert len(p.hand) == 2


def test_wells_fargo_draws_three_cards():
    deck = Deck([BangCard(), BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p = Player("A")
    gm.add_player(p)
    WellsFargoCard().play(p, game=gm)
    assert len(p.hand) == 3


def test_panic_steals_card():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.hand.append(BangCard())
    PanicCard().play(p2, p1, game=gm)
    assert len(p1.hand) == 1
    assert len(p2.hand) == 0


def test_cat_balou_discards_card():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.hand.append(BangCard())
    CatBalouCard().play(p2, game=gm)
    assert len(p2.hand) == 0
    assert len(gm.discard_pile) == 1


def test_indians_forces_bang_or_damage():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    p2.hand.append(BangCard())
    IndiansCard().play(p1, p1, game=gm)
    assert len(p2.hand) == 0
    assert p3.health == p3.max_health - 1


def test_duel_discards_bang_until_damage():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.hand.append(BangCard())
    DuelCard().play(p2, p1, game=gm)
    assert p1.health == p1.max_health - 1
    assert len(p2.hand) == 0


def test_general_store_gives_each_player_card():
    deck = Deck([BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    GeneralStoreCard().play(p1, p1, game=gm)
    assert len(p1.hand) == 1
    assert len(p2.hand) == 1


def test_general_store_selection_order():
    deck = Deck([])
    c1, c2, c3 = BangCard(), BeerCard(), GatlingCard()
    deck.cards = deque([c3, c2, c1])
    gm = GameManager(deck=deck)
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    GeneralStoreCard().play(p1, p1, game=gm)
    assert p1.hand == [c3]
    assert p2.hand == [c2]
    assert p3.hand == [c1]


def test_general_store_allows_player_choice():
    deck = Deck([])
    c1, c2, c3 = BangCard(), BeerCard(), GatlingCard()
    deck.cards = deque([c3, c2, c1])
    gm = GameManager(deck=deck)
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    GeneralStoreCard().play(p1, p1, game=gm, choices=[1, 0, 0])
    assert p1.hand == [c2]
    assert p2.hand == [c3]
    assert p3.hand == [c1]


def test_saloon_heals_everyone():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.health -= 1
    p2.health -= 1
    SaloonCard().play(p1, p1, game=gm)
    assert p1.health == p1.max_health
    assert p2.health == p2.max_health


def test_gatling_hits_all_opponents():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    GatlingCard().play(p1, p1, game=gm)
    assert p2.health == p2.max_health - 1
    assert p3.health == p3.max_health - 1


def test_cat_balou_allows_choice_from_hand():
    gm = GameManager(deck=Deck([]))
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    c1, c2 = BangCard(), BeerCard()
    target.hand.extend([c1, c2])
    CatBalouCard().play(target, game=gm, hand_idx=1)
    assert gm.discard_pile[-1] is c2
    assert target.hand == [c1]


def test_cat_balou_allows_choice_from_equipment():
    from bang_py.cards.barrel import BarrelCard

    gm = GameManager(deck=Deck([]))
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    BarrelCard().play(target)
    CatBalouCard().play(target, game=gm, equip_name="Barrel")
    assert "Barrel" not in target.equipment
    assert isinstance(gm.discard_pile[-1], BarrelCard)


def test_panic_allows_choice_from_hand():
    gm = GameManager(deck=Deck([]))
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    c1, c2 = BangCard(), BeerCard()
    target.hand.extend([c1, c2])
    PanicCard().play(target, attacker, game=gm, hand_idx=0)
    assert attacker.hand[-1] is c1
    assert target.hand == [c2]


def test_panic_allows_choice_from_equipment():
    from bang_py.cards.scope import ScopeCard

    gm = GameManager(deck=Deck([]))
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    ScopeCard().play(target)
    PanicCard().play(target, attacker, game=gm, equip_name="Scope")
    assert "Scope" not in target.equipment
    assert any(isinstance(c, ScopeCard) for c in attacker.hand)
