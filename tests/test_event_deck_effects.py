from collections import deque

from bang_py.events.event_decks import (
    EventCard,
    _thirst,
    _fistful,
    _judge,
    _ghost_town,
    _peyote,
    _ricochet,
    _vendetta,
    _abandoned_mine,
    _hard_liquor,
    _law_of_the_west,
    _shootout,
    _blessing,
    _gold_rush,
    _sermon,
    _hangover,
    _ambush_event,
    _blood_brothers,
    _ranch,
    _high_noon,
    create_high_noon_deck,
    create_fistful_deck,
)
from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards.roles import (
    SheriffRoleCard,
    OutlawRoleCard,
)
from bang_py.cards import BangCard, BeerCard, MissedCard, BarrelCard
from bang_py.cards.events import (
    DeadManEventCard,
    BloodBrothersEventCard,
    CurseEventCard,
    TheDaltonsEventCard,
    TheDoctorEventCard,
    TheReverendEventCard,
    TrainArrivalEventCard,
    HandcuffsEventCard,
)
from bang_py.helpers import has_ability
from bang_py.characters.black_jack import BlackJack
from bang_py.characters.paul_regret import PaulRegret
from bang_py.deck import Deck


def test_thirst_event_draw_one():
    gm = GameManager()
    gm.event_deck = deque([EventCard("Thirst", _thirst, "")])
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 1


def test_fistful_event_bangs_by_hand():
    deck = Deck([BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    p.hand = [BangCard(), BangCard()]
    gm.event_deck = deque([EventCard("A Fistful of Cards", _fistful, "")])
    gm.turn_order = [0]
    gm.current_turn = 0
    gm._begin_turn()
    gm.end_turn()
    assert p.health == p.max_health - 4


def _enable_no_bang(game: GameManager) -> None:
    game.event_flags.update(no_bang=True)


def test_sermon_event_blocks_bang():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = deque([EventCard("The Sermon", _enable_no_bang, "")])
    gm.draw_event_card()
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 1
    assert outlaw.health == outlaw.max_health


def test_hangover_disables_abilities():
    from bang_py.characters.jesse_jones import JesseJones

    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard(), character=JesseJones())
    gm.add_player(p)
    assert has_ability(p, JesseJones)
    gm.event_deck = deque([EventCard("Hangover", _hangover, "")])
    gm.draw_event_card()
    assert not has_ability(p, JesseJones)


def test_judge_prevents_beer_play():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(sheriff)
    gm.event_deck = deque([EventCard("The Judge", _judge, "")])
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
    gm.event_deck = deque([EventCard("Ghost Town", _ghost_town, "")])
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    gm._begin_turn()  # sheriff first turn
    gm.end_turn()  # end sheriff -> outlaw first turn (still dead)
    gm.end_turn()  # end outlaw -> sheriff second turn -> draw event
    gm.end_turn()  # end sheriff -> outlaw revived turn
    assert outlaw.is_alive()
    assert len(outlaw.hand) == 3


def test_ghost_town_players_disappear_next_event():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    outlaw.take_damage(outlaw.health)
    gm.event_deck = deque([
        EventCard("Ghost Town", _ghost_town, ""),
        EventCard("Thirst", _thirst, ""),
    ])
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    gm._begin_turn()  # sheriff first turn
    gm.end_turn()  # outlaw first turn (dead)
    gm.end_turn()  # sheriff second -> ghost town drawn
    gm.end_turn()  # outlaw revived
    assert outlaw.is_alive()
    gm.end_turn()  # end outlaw -> sheriff third -> next event
    gm.end_turn()  # sheriff end -> outlaw disappears
    assert not outlaw.is_alive()


def test_blessing_overrides_suit():
    deck = Deck([BangCard(suit="Clubs"), BangCard(suit="Spades")])
    gm = GameManager(deck=deck)
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([EventCard("Blessing", _blessing, "")])
    gm.draw_event_card()
    gm.draw_phase(p)
    assert all(c.suit == "Hearts" for c in p.hand)


def test_gold_rush_reverses_turn_order():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    gm.turn_order = [0, 1, 2]
    gm.current_turn = 0
    gm.event_deck = deque([EventCard("Gold Rush", _gold_rush, "")])
    gm.draw_event_card()
    gm.end_turn()
    assert gm.players[gm.turn_order[gm.current_turn]] is p3


def test_vendetta_outlaw_range_bonus():
    gm = GameManager()
    outlaw = Player("Out", role=OutlawRoleCard())
    target = Player("T")
    gm.add_player(outlaw)
    gm.add_player(target)
    gm.event_deck = deque([EventCard("Vendetta", _vendetta, "")])
    gm.draw_event_card()
    assert outlaw.attack_range == 2


def test_sermon_blocks_bang_real():
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = deque([EventCard("The Sermon", _sermon, "")])
    gm.draw_event_card()
    sheriff.hand.append(BangCard())
    gm.play_card(sheriff, sheriff.hand[0], outlaw)
    assert len(sheriff.hand) == 1
    assert outlaw.health == outlaw.max_health


def test_ricochet_discards_equipment():
    gm = GameManager()
    shooter = Player("P1")
    target = Player("P2")
    gm.add_player(shooter)
    gm.add_player(target)
    BarrelCard().play(target)
    shooter.hand.append(BangCard())
    gm.event_deck = deque([EventCard("Ricochet", _ricochet, "")])
    gm.draw_event_card()
    assert gm.ricochet_shoot(shooter, target, "Barrel")
    assert "Barrel" not in target.equipment


def test_ricochet_can_be_missed():
    gm = GameManager()
    shooter = Player("P1")
    target = Player("P2")
    gm.add_player(shooter)
    gm.add_player(target)
    BarrelCard().play(target)
    target.hand.append(MissedCard())
    shooter.hand.append(BangCard())
    gm.event_deck = deque([EventCard("Ricochet", _ricochet, "")])
    gm.draw_event_card()
    assert not gm.ricochet_shoot(shooter, target, "Barrel")
    assert "Barrel" in target.equipment
    assert not target.hand


def test_ambush_sets_distance_one():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = deque([EventCard("Ambush", _ambush_event, "")])
    gm.draw_event_card()
    assert p1.distance_to(p2) == 1


def test_ranch_discard_and_redraw():
    deck = Deck([])
    deck.cards = [BangCard(), BangCard(), BangCard(), BangCard()]
    gm = GameManager(deck=deck)
    p1 = Player("A")
    gm.add_player(p1)
    gm.event_deck = deque([EventCard("Ranch", _ranch, "")])
    gm.draw_event_card()
    p1.hand = [BangCard(), MissedCard()]
    gm.draw_phase(p1, ranch_discards=[2, 3])
    assert len(p1.hand) == 4


def test_high_noon_start_damage():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([EventCard("High Noon", _high_noon, "")])
    gm.turn_order = [0]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn()
    assert p.health == p.max_health - 1


def test_blood_brothers_transfer_during_turn():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.health -= 1
    gm.event_deck = deque([EventCard("Blood Brothers", _blood_brothers, "")])
    gm.turn_order = [0]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn(blood_target=p2)
    assert p1.health == p1.max_health - 1
    assert p2.health == p2.max_health


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
    assert gm.current_event is None
    assert gm.event_deck[-1].name == "A Fistful of Cards"


def test_peyote_extra_draw():
    deck = Deck([])
    deck.cards = [
        BangCard(suit="Hearts"),
        BangCard(suit="Clubs"),
        BangCard(suit="Diamonds"),
    ]
    gm = GameManager(deck=deck)
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([EventCard("Peyote", _peyote, "")])
    gm.draw_event_card()
    gm.draw_phase(p, peyote_guesses=["red", "black", "red"])
    assert len(p.hand) == 3


def test_abandoned_mine_uses_discard_pile_and_deck_top():
    deck = Deck([MissedCard()])
    gm = GameManager(deck=deck)
    p1 = Player("A")
    gm.add_player(p1)
    gm.discard_pile.append(BangCard())
    gm.event_deck = deque([EventCard("Abandoned Mine", _abandoned_mine, "")])
    gm.draw_event_card()
    p1.health = 1
    gm.draw_phase(p1)
    assert isinstance(p1.hand[0], BangCard)
    p1.hand.append(MissedCard())
    gm.discard_phase(p1)
    assert isinstance(gm.deck.cards[0], MissedCard)


def test_daltons_discards_equipment():
    from bang_py.cards import MustangCard

    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    MustangCard().play(p1)
    MustangCard().play(p2)
    gm.event_deck = deque([TheDaltonsEventCard()])
    gm.draw_event_card()
    assert not p1.equipment
    assert not p2.equipment


def test_doctor_heals_lowest():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.health -= 2
    p2.health -= 1
    gm.event_deck = deque([TheDoctorEventCard()])
    gm.draw_event_card()
    assert p1.health == p1.max_health - 1
    assert p2.health == p2.max_health - 1


def test_reverend_blocks_beer():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([TheReverendEventCard()])
    gm.draw_event_card()
    p.health -= 1
    p.hand.append(BeerCard())
    gm.play_card(p, p.hand[0])
    assert p.health == p.max_health - 1


def test_train_arrival_draw_three():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([TrainArrivalEventCard()])
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 3


def test_hard_liquor_skip_draw_to_heal():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([EventCard("Hard Liquor", _hard_liquor, "")])
    gm.draw_event_card()
    p.health -= 1
    gm.draw_phase(p, skip_heal=True)
    assert p.health == p.max_health
    assert not p.hand


def test_law_of_west_plays_second_card():
    deck = Deck([])
    deck.cards = [BeerCard(), BeerCard()]
    gm = GameManager(deck=deck)
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([EventCard("Law of the West", _law_of_the_west, "")])
    gm.draw_event_card()
    gm.draw_phase(p)
    assert len(p.hand) == 1


def test_shootout_allows_multiple_bangs():
    gm = GameManager()
    p1 = Player("Sheriff", role=SheriffRoleCard())
    p2 = Player("Outlaw")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = deque([EventCard("Shootout", _shootout, "")])
    gm.draw_event_card()
    p1.hand.extend([BangCard(), BangCard()])
    gm.play_card(p1, p1.hand[0], p2)
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 2


def test_handcuffs_limits_suit_played():
    deck = Deck([])
    deck.cards = [BangCard(suit="Hearts"), BeerCard(suit="Spades")]
    gm = GameManager(deck=deck)
    p1 = Player("Sheriff", role=SheriffRoleCard())
    p2 = Player("Outlaw")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.event_deck = deque([HandcuffsEventCard()])
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    gm.draw_event_card()
    gm._begin_turn()
    idx = 0 if p1.hand[0].suit == "Hearts" else 1
    gm.play_card(p1, p1.hand[idx], p2)
    assert len(p1.hand) == 1
    gm.play_card(p1, p1.hand[0], p2)
    assert len(p1.hand) == 1
    assert p1.hand[0].suit == "Spades"


def test_event_deck_order_high_noon():
    gm = GameManager(expansions=["high_noon"])
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.start_game(deal_roles=False)
    assert gm.current_event is None
    assert gm.event_deck[-1].name == "High Noon"


def test_event_sequence_progresses_each_sheriff_turn():
    e1 = EventCard("E1", lambda g: g.event_flags.update(test=1))
    e2 = EventCard("E2", lambda g: g.event_flags.update(test=2))
    gm = GameManager()
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.event_deck = deque([e1, e2])
    gm.start_game(deal_roles=False)
    assert gm.current_event is None
    gm.end_turn()  # sheriff end -> outlaw turn
    gm.end_turn()  # outlaw end -> sheriff second turn -> first event
    assert gm.current_event.name == "E1"
    gm.end_turn()  # sheriff end -> outlaw
    gm.end_turn()  # outlaw end -> sheriff third turn -> next event
    assert gm.current_event.name == "E2"


def test_dead_man_revives_first_eliminated():
    deck = Deck([BangCard(), BeerCard(), MissedCard(), BangCard(), BeerCard(), MissedCard()])
    gm = GameManager(deck=deck)
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.start_game(deal_roles=False)
    outlaw.take_damage(outlaw.health)
    gm.on_player_damaged(outlaw)
    gm.event_deck = deque([DeadManEventCard()])
    gm.draw_event_card()
    gm.end_turn()  # sheriff end -> outlaw turn and revive
    assert outlaw.health == 2
    assert len(outlaw.hand) == 2


def test_blood_brothers_life_transfer():
    gm = GameManager()
    donor = Player("A")
    target = Player("B")
    gm.add_player(donor)
    gm.add_player(target)
    gm.event_deck = deque([BloodBrothersEventCard()])
    gm.draw_event_card()
    target.take_damage(1)
    assert gm.blood_brothers_transfer(donor, target)
    assert donor.health == donor.max_health - 1
    assert target.health == target.max_health


def test_curse_overrides_to_spades():
    deck = Deck([BangCard(suit="Hearts")])
    gm = GameManager(deck=deck)
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([CurseEventCard()])
    gm.draw_event_card()
    gm.draw_phase(p)
    assert p.hand[0].suit == "Spades"


def _no_draw(game: GameManager) -> None:
    game.event_flags["no_draw"] = True


def test_no_draw_skips_draw_phase():
    gm = GameManager()
    p = Player("Sheriff", role=SheriffRoleCard())
    gm.add_player(p)
    gm.event_deck = deque([EventCard("Skip", _no_draw, "")])
    gm.draw_event_card()
    gm.draw_phase(p)
    assert not p.hand


def test_new_identity_character_swap():
    gm = GameManager()
    p = Player("S", role=SheriffRoleCard(), character=PaulRegret())
    gm.add_player(p)
    p.metadata.unused_character = BlackJack()
    p.reset_stats()
    gm.turn_order = [0]
    gm.current_turn = 0
    gm.event_flags["new_identity"] = True
    gm._begin_turn()
    assert isinstance(p.character, BlackJack)
    assert p.health == 2
