from bang_py.deck_factory import create_standard_deck
from bang_py.deck_factory import create_standard_deck
from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards import (
    PunchCard,
    HideoutCard,
    BinocularsCard,
    BuffaloRifleCard,
    WhiskyCard,
    HighNoonCard,
    PonyExpressCard,
    TequilaCard,
    BeerCard,
)
from bang_py.characters import PixiePete, SeanMallory, TequilaJoe


def test_dodge_city_cards_added():
    deck = create_standard_deck(["dodge_city"])
    types = {type(c) for c in deck.cards}
    assert {PunchCard, HideoutCard, BinocularsCard, BuffaloRifleCard} <= types


def test_whisky_heals_two():
    gm = GameManager()
    p1 = Player("A")
    gm.add_player(p1)
    card = WhiskyCard()
    p1.health = p1.max_health - 2
    p1.hand.append(card)
    gm.play_card(p1, card, p1)
    assert p1.health == p1.max_health


def test_high_noon_draws_card_for_all():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.deck.cards.extend([PunchCard(), PunchCard()])
    card = HighNoonCard()
    p1.hand.append(card)
    gm.play_card(p1, card, p1)
    assert len(p1.hand) == 1
    assert len(p2.hand) == 1


def test_pony_express_draws_three():
    gm = GameManager()
    p1 = Player("A")
    gm.add_player(p1)
    card = PonyExpressCard()
    p1.hand.append(card)
    gm.play_card(p1, card)
    assert len(p1.hand) == 3


def test_tequila_heals_one():
    gm = GameManager()
    p1 = Player("A")
    gm.add_player(p1)
    card = TequilaCard()
    p1.hand.append(card)
    p1.health -= 1
    gm.play_card(p1, card, p1)
    assert p1.health == p1.max_health


def test_pixie_pete_draws_three():
    gm = GameManager()
    pp = Player("Pixie", character=PixiePete())
    gm.add_player(pp)
    gm.draw_phase(pp)
    assert len(pp.hand) == 3


def test_sean_mallory_unlimited_hand():
    gm = GameManager()
    sm = Player("Sean", character=SeanMallory())
    gm.add_player(sm)
    sm.hand = [PunchCard()] * 5
    gm.discard_phase(sm)
    assert len(sm.hand) == 5


def test_tequila_joe_beer_heals_two():
    gm = GameManager()
    tj = Player("TJ", character=TequilaJoe())
    gm.add_player(tj)
    gm.add_player(Player("Other1"))
    gm.add_player(Player("Other2"))
    card = BeerCard()
    tj.health -= 2
    tj.hand.append(card)
    gm.play_card(tj, card, tj)
    assert tj.health == tj.max_health

