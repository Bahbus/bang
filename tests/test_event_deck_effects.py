from bang_py.event_decks import (
    EventCard,
    _thirst,
    _fistful,
    _judge,
    _ghost_town,
    _peyote,
    _ricochet,
    _river,
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


def _enable_no_bang(game: GameManager) -> None:
    game.event_flags.update(no_bang=True)


def test_sermon_event_blocks_bang():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [EventCard("The Sermon", _enable_no_bang, "")]
    gm.draw_event_card()
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 1
    assert outlaw.health == outlaw.max_health


def _enable_no_beer(game: GameManager) -> None:
    game.event_flags.update(no_beer=True)


def test_hangover_event_disables_beer():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(sheriff)
    gm.event_deck = [EventCard("Hangover", _enable_no_beer, "")]
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


def test_ghost_town_players_disappear_next_event():
    gm = GameManager()
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    outlaw.take_damage(outlaw.health)
    gm.event_deck = [
        EventCard("Ghost Town", _ghost_town, ""),
        EventCard("Thirst", _thirst, ""),
    ]
    gm.draw_event_card()
    assert outlaw.is_alive()
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    gm._begin_turn()
    assert not outlaw.is_alive()
    assert len(gm.turn_order) == 1


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


def test_ricochet_hits_next_player():
    gm = GameManager()
    p1 = Player("P1")
    p2 = Player("P2")
    p3 = Player("P3")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    gm.event_deck = [EventCard("Ricochet", _ricochet, "")]
    gm.draw_event_card()
    p1.hand.append(BangCard())
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 1
    assert p3.health == p3.max_health - 1


def test_river_passes_discard_left():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    gm.event_deck = [EventCard("The River", _river, "")]
    gm.draw_event_card()
    card = BangCard()
    p1.hand.append(card)
    gm.discard_card(p1, card)
    assert card in p2.hand
    assert card not in gm.discard_pile


def test_peyote_extra_draw():
    gm = GameManager()
    p = Player("Sheriff", role=Role.SHERIFF)
    gm.add_player(p)
    gm.event_deck = [EventCard("Peyote", _peyote, "")]
    gm.draw_event_card()
    gm.draw_card(p)
    assert len(p.hand) == 2
