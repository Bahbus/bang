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
    _abandoned_mine,
    _hard_liquor,
    _law_of_the_west,
    _cattle_drive,
    _shootout,
    _blessing,
    _gold_rush,
    _siesta,
    _sermon,
    _hangover,
    _ambush_event,
    _ranch,
    _prison_break,
    _high_noon,
    _high_stakes,
    create_high_noon_deck,
    create_fistful_deck,
    _daltons_event,
    _doctor_event,
    _reverend_event,
    _train_arrival_event,
)
from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards.roles import (
    SheriffRoleCard,
    DeputyRoleCard,
    OutlawRoleCard,
    RenegadeRoleCard,
)
from bang_py.cards import BangCard, BeerCard, MissedCard
from bang_py.cards.jail import JailCard
from bang_py.deck import Deck


def test_thirst_event_draw_one():
    gm = GameManager()
    gm.event_deck = [EventCard("Thirst", _thirst, "")]
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 1


def test_fistful_event_damage_by_hand():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
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
    sheriff = Player("Sheriff", role=SheriffRoleCard())
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
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(sheriff)
    gm.event_deck = [EventCard("Hangover", _enable_no_beer, "")]
    gm.draw_event_card()
    sheriff.health -= 1
    sheriff.hand.append(BeerCard())
    gm.play_card(sheriff, sheriff.hand[0])
    assert sheriff.health == sheriff.max_health - 1


def test_judge_prevents_beer_play():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
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
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    outlaw.take_damage(outlaw.health)
    gm.event_deck = [EventCard("Ghost Town", _ghost_town, "")]
    gm.draw_event_card()
    assert outlaw.health == 1


def test_ghost_town_players_disappear_next_event():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
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
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [EventCard("Bounty", _bounty, "")]
    gm.draw_event_card()
    outlaw.health = 1
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 2


def test_blessing_heals_everyone():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.health -= 1
    p2.health -= 1
    gm.event_deck = [EventCard("Blessing", _blessing, "")]
    gm.draw_event_card()
    assert p1.health == p1.max_health
    assert p2.health == p2.max_health


def test_gold_rush_draws_three():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("Gold Rush", _gold_rush, "")]
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 3


def test_siesta_draws_three():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("Siesta", _siesta, "")]
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 3


def test_vendetta_outlaw_range_bonus():
    gm = GameManager()
    outlaw = Player("Out", role=OutlawRoleCard())
    target = Player("T")
    gm.add_player(outlaw)
    gm.add_player(target)
    gm.event_deck = [EventCard("Vendetta", _vendetta, "")]
    gm.draw_event_card()
    assert outlaw.attack_range == 2


def test_sermon_blocks_bang_real():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [EventCard("The Sermon", _sermon, "")]
    gm.draw_event_card()
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 1
    assert outlaw.health == outlaw.max_health


def test_hangover_no_beer_real():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("Hangover", _hangover, "")]
    gm.draw_event_card()
    p.health -= 1
    p.hand.append(BeerCard())
    gm.play_card(p, p.hand[0])
    assert p.health == p.max_health - 1


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


def test_ambush_disables_auto_miss():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [EventCard("Ambush", _ambush_event, "")]
    gm.draw_event_card()
    p1.hand.append(BangCard())
    p2.hand.append(MissedCard())
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 1
    assert isinstance(p2.hand[0], MissedCard)


def test_ranch_heals_everyone():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.health -= 1
    p2.health -= 1
    gm.event_deck = [EventCard("Ranch", _ranch, "")]
    gm.draw_event_card()
    assert p1.health == p1.max_health
    assert p2.health == p2.max_health


def test_prison_break_discards_jail():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    jail = JailCard()
    p.equipment["Jail"] = jail
    gm.event_deck = [EventCard("Prison Break", _prison_break, "")]
    gm.turn_order = [0]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn()
    assert "Jail" not in p.equipment
    assert jail in gm.discard_pile


def test_high_noon_start_damage():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("High Noon", _high_noon, "")]
    gm.turn_order = [0]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn()
    assert p.health == p.max_health - 1


def test_high_stakes_allows_multiple_bangs():
    gm = GameManager()
    p1 = Player("Sheriff", role=SheriffRoleCard())
    p2 = Player("Outlaw")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [EventCard("High Stakes", _high_stakes, "")]
    gm.draw_event_card()
    p1.hand.extend([BangCard(), BangCard()])
    gm.play_card(p1, p1.hand[0], p2)
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 2


def test_high_noon_deck_contents_full_list():
    names = {card.name for card in create_high_noon_deck()}
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


def test_fistful_deck_contents_full_list():
    names = {card.name for card in create_fistful_deck()}
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


def test_event_deck_order_fistful():
    gm = GameManager(expansions=["fistful_of_cards"])
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.start_game(deal_roles=False)
    assert gm.current_event is not None
    assert gm.event_deck[-1].name == "A Fistful of Cards"


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
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("Peyote", _peyote, "")]
    gm.draw_event_card()
    gm.draw_card(p)
    assert len(p.hand) == 2


def test_abandoned_mine_all_draw():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [EventCard("Abandoned Mine", _abandoned_mine, "")]
    gm.draw_event_card()
    assert len(p1.hand) == 1
    assert len(p2.hand) == 1


def test_daltons_all_draw():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [EventCard("The Daltons", _daltons_event, "")]
    gm.draw_event_card()
    assert len(p1.hand) == 1
    assert len(p2.hand) == 1

def test_reverend_limits_hand_size():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("The Reverend", _reverend_event, "")]
    p.hand = [BangCard(), BangCard(), BangCard()]
    gm.draw_event_card()
    gm.discard_phase(p)
    assert len(p.hand) == 2

def test_train_arrival_all_draw():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [EventCard("Train Arrival", _train_arrival_event, "")]
    gm.draw_event_card()
    assert len(p1.hand) == 1
    assert len(p2.hand) == 1


def test_hard_liquor_beer_heals_two():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.add_player(Player("Other"))
    gm.add_player(Player("Third"))
    gm.event_deck = [EventCard("Hard Liquor", _hard_liquor, "")]
    gm.draw_event_card()
    p.health -= 2
    p.hand.append(BeerCard())
    gm.play_card(p, p.hand[0])
    assert p.health == p.max_health


def test_law_of_west_unlimited_range():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = [EventCard("Law of the West", _law_of_the_west, "")]
    gm.draw_event_card()
    assert p.attack_range == 99


def test_cattle_drive_discards_one_each():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.hand.append(BangCard())
    gm.event_deck = [EventCard("Cattle Drive", _cattle_drive, "")]
    gm.draw_event_card()
    assert not p1.hand
    assert not p2.hand


def test_shootout_allows_multiple_bangs():
    gm = GameManager()
    p1 = Player("Sheriff", role=SheriffRoleCard())
    p2 = Player("Outlaw")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = [EventCard("Shootout", _shootout, "")]
    gm.draw_event_card()
    p1.hand.extend([BangCard(), BangCard()])
    gm.play_card(p1, p1.hand[0], p2)
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 2


def test_event_deck_order_high_noon():
    gm = GameManager(expansions=["high_noon"])
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.start_game(deal_roles=False)
    assert gm.current_event is not None
    assert gm.event_deck[-1].name == "High Noon"


def test_event_sequence_progresses_each_sheriff_turn():
    e1 = EventCard("E1", lambda g: g.event_flags.update(test=1))
    e2 = EventCard("E2", lambda g: g.event_flags.update(test=2))
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = [e1, e2]
    gm.start_game(deal_roles=False)
    assert gm.current_event.name == "E1"
    gm.end_turn()  # sheriff end -> outlaw turn
    gm.end_turn()  # outlaw end -> sheriff turn, draw next
    assert gm.current_event.name == "E2"
