from collections import deque

from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard, OutlawRoleCard
from bang_py.events.event_decks import create_high_noon_deck, create_fistful_deck
from bang_py.cards.events import (
    HandcuffsEventCard,
    NewIdentityEventCard,
    LassoEventCard,
    SniperEventCard,
    RussianRouletteEventCard,
)
from bang_py.cards import BangCard, MissedCard
from bang_py.deck import Deck


def test_handcuffs_restricts_suit():
    deck = Deck([])
    deck.cards = [BangCard(suit="Hearts"), BangCard(suit="Spades")]
    gm = GameManager(deck=deck)
    sheriff = Player("S", role=SheriffRoleCard())
    outlaw = Player("O", role=OutlawRoleCard())
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = deque([HandcuffsEventCard()])
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn()
    idx = 0 if sheriff.hand[0].suit == "Hearts" else 1
    gm.play_card(sheriff, sheriff.hand[idx], outlaw)
    assert sheriff.metadata.bangs_played == 1
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 1


def test_new_identity_event_redraw():
    deck = Deck([BangCard(), BangCard(), BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p = Player("P", role=SheriffRoleCard())
    gm.add_player(p)
    p.hand = [BangCard(), BangCard()]
    gm.event_deck = deque([NewIdentityEventCard()])
    gm.draw_event_card()
    assert len(p.hand) == 2


def test_lasso_event_ignores_equipment():
    from bang_py.cards import MustangCard
    gm = GameManager()
    a = Player("A")
    b = Player("B")
    gm.add_player(a)
    gm.add_player(b)
    MustangCard().play(b)
    assert a.distance_to(b) > 1
    gm.event_deck = deque([LassoEventCard()])
    gm.draw_event_card()
    assert a.distance_to(b) == 1


def test_sniper_event_allows_special_bang():
    gm = GameManager()
    p = Player("P", role=SheriffRoleCard())
    t = Player("T")
    gm.add_player(p)
    gm.add_player(t)
    gm.event_deck = deque([SniperEventCard()])
    gm.draw_event_card()
    p.hand.extend([BangCard(), BangCard()])
    gm.play_card(p, p.hand[0], t)
    gm.play_card(p, p.hand[0], t)
    assert t.health == t.max_health - 1
    assert "sniper" in gm.event_flags


def test_sniper_event_double_bang_damage():
    gm = GameManager()
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    attacker.hand.extend([BangCard(), BangCard()])
    gm.event_deck = deque([SniperEventCard()])
    gm.draw_event_card()
    attacker.metadata.use_sniper = True
    gm.play_card(attacker, attacker.hand[0], target)
    assert not attacker.hand
    assert target.health == target.max_health - 1
    assert len([c for c in gm.discard_pile if isinstance(c, BangCard)]) == 2


def test_russian_roulette_players_discard_missed():
    gm = GameManager()
    s = Player("S", role=SheriffRoleCard())
    o = Player("O")
    gm.add_player(s)
    gm.add_player(o)
    o.hand.append(MissedCard())
    gm.event_deck = deque([RussianRouletteEventCard()])
    gm.draw_event_card()
    assert s.health == s.max_health - 2
    assert o.health == o.max_health
    assert len(o.hand) == 1


def test_rev_carabine_range():
    from bang_py.cards import RevCarabineCard
    p = Player("P")
    RevCarabineCard().play(p)
    assert p.attack_range == 4


def test_high_noon_deck_contents():
    names = {card.card_name for card in create_high_noon_deck()}
    assert len(names) == 15
    assert names == {
        "Blessing",
        "Curse",
        "Ghost Town",
        "Gold Rush",
        "Hangover",
        "High Noon",
        "Shootout",
        "The Daltons",
        "The Doctor",
        "The Reverend",
        "The Sermon",
        "Thirst",
        "Train Arrival",
        "Handcuffs",
        "New Identity",
    }


def test_fistful_deck_contents():
    names = {card.card_name for card in create_fistful_deck()}
    assert len(names) == 15
    assert names == {
        "A Fistful of Cards",
        "Abandoned Mine",
        "Ambush",
        "Blood Brothers",
        "Dead Man",
        "Hard Liquor",
        "Lasso",
        "Law of the West",
        "Peyote",
        "Ranch",
        "Ricochet",
        "Russian Roulette",
        "Sniper",
        "The Judge",
        "Vendetta",
    }
