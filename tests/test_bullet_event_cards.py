from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard, OutlawRoleCard
from bang_py.event_decks import create_high_noon_deck, create_fistful_deck
from bang_py.cards.events import (
    HandcuffsEventCard,
    NewIdentityEventCard,
    LassoEventCard,
    SniperEventCard,
    RussianRouletteEventCard,
)
from bang_py.cards import BangCard
from bang_py.deck import Deck


def test_handcuffs_event_skips_turn():
    gm = GameManager()
    sheriff = Player("S", role=SheriffRoleCard())
    outlaw = Player("O", role=OutlawRoleCard())
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [HandcuffsEventCard()]
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn()
    assert gm.players[gm.turn_order[gm.current_turn]] is outlaw


def test_new_identity_event_redraw():
    deck = Deck([BangCard(), BangCard(), BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p = Player("P", role=SheriffRoleCard())
    gm.add_player(p)
    p.hand = [BangCard(), BangCard()]
    gm.event_deck = [NewIdentityEventCard()]
    gm.draw_event_card()
    assert len(p.hand) == 2


def test_lasso_event_transfers_card():
    gm = GameManager()
    a = Player("A")
    b = Player("B")
    gm.add_player(a)
    gm.add_player(b)
    b.hand.append(BangCard())
    gm.event_deck = [LassoEventCard()]
    gm.draw_event_card()
    assert isinstance(a.hand[0], BangCard)
    assert not b.hand


def test_sniper_event_flag_set_without_range_change():
    gm = GameManager()
    p = Player("P", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [SniperEventCard()]
    gm.draw_event_card()
    assert "sniper" in gm.event_flags
    assert p.attack_range == 1


def test_sniper_event_double_bang_damage():
    gm = GameManager()
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    attacker.hand.extend([BangCard(), BangCard()])
    gm.event_deck = [SniperEventCard()]
    gm.draw_event_card()
    attacker.metadata.use_sniper = True
    gm.play_card(attacker, attacker.hand[0], target)
    assert not attacker.hand
    assert target.health == target.max_health - 1
    assert len([c for c in gm.discard_pile if isinstance(c, BangCard)]) == 2


def test_russian_roulette_event_damage():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [RussianRouletteEventCard()]
    gm.draw_event_card()
    assert p1.health == p1.max_health - 1
    assert p2.health == p2.max_health - 1


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

