from bang_py.event_decks import (
    EventCard,
    _thirst,
    _fistful,
    _judge,
    _ghost_town,
    _bounty,
    _vendetta,
)
from bang_py.game_manager import GameManager
from bang_py.player import Player, Role
from bang_py.cards import BangCard, BeerCard
from bang_py.deck import Deck


def test_thirst_event_draw_one():
    gm = GameManager()
    gm.event_deck = [EventCard("Thirst", _thirst, "")]
    p = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(p)
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 1


def test_fistful_event_damage_by_hand():
    gm = GameManager()
    p = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(p)
    p.hand = [BangCard(), BangCard()]
    gm.event_deck = [EventCard("A Fistful of Cards", _fistful, "")]
    gm.turn_order = [0]
    gm.current_turn = 0
    gm._begin_turn()
    assert p.health == p.max_health - 2


def test_sermon_event_blocks_bang():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [EventCard("The Sermon", lambda g: g.event_flags.update(no_bang=True), "")]
    gm.draw_event_card()
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 1
    assert outlaw.health == outlaw.max_health


def test_hangover_event_disables_beer():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(sheriff)
    gm.event_deck = [EventCard("Hangover", lambda g: g.event_flags.update(no_beer=True), "")]
    gm.draw_event_card()
    sheriff.health -= 1
    sheriff.hand.append(BeerCard())
    gm.play_card(sheriff, sheriff.hand[0])
    assert sheriff.health == sheriff.max_health - 1


def test_judge_prevents_beer_play():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(sheriff)
    gm.event_deck = [EventCard("The Judge", _judge, "")]
    gm.draw_event_card()
    sheriff.health -= 1
    sheriff.hand.append(BeerCard())
    gm.play_card(sheriff, sheriff.hand[0])
    assert sheriff.health == sheriff.max_health - 1
    assert len(gm.discard_pile) == 1


def test_ghost_town_revives_players():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    outlaw.take_damage(outlaw.health)
    gm.event_deck = [EventCard("Ghost Town", _ghost_town, "")]
    gm.draw_event_card()
    assert outlaw.health == 1


def test_bounty_rewards_elimination():
    deck = Deck([BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [EventCard("Bounty", _bounty, "")]
    gm.draw_event_card()
    outlaw.health = 1
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 2


def test_vendetta_outlaw_range_bonus():
    gm = GameManager()
    outlaw = Player("Out", role=Role.OUTLAW)
    target = Player("T")
    gm.add_player(outlaw)
    gm.add_player(target)
    gm.event_deck = [EventCard("Vendetta", _vendetta, "")]
    gm.draw_event_card()
    assert outlaw.attack_range == 2
