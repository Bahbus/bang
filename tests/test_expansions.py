from bang_py.deck_factory import create_standard_deck
from bang_py.game_manager import GameManager
from bang_py.player import Player, Role
from bang_py.deck import Deck
from bang_py.cards import (
    PunchCard,
    HideoutCard,
    BinocularsCard,
    BuffaloRifleCard,
    PepperboxCard,
    HowitzerCard,
    WhiskyCard,
    HighNoonCard,
    PonyExpressCard,
    TequilaCard,
    BeerCard,
    BarrelCard,
    BangCard,
    CatBalouCard,
    PanicCard,
    IndiansCard,
    StagecoachCard,
    MissedCard,
)
from bang_py.characters import (
    PixiePete,
    SeanMallory,
    TequilaJoe,
    BillNoface,
    BelleStar,
    ChuckWengam,
    DocHolyday,
    ElenaFuente,
    MollyStark,
    PatBrennan,
    UncleWill,
    JohnnyKisch,
    ClausTheSaint,
)


def test_dodge_city_cards_added():
    deck = create_standard_deck(["dodge_city"])
    types = {type(c) for c in deck.cards}
    assert {
        PunchCard,
        HideoutCard,
        BinocularsCard,
        BuffaloRifleCard,
        PepperboxCard,
        HowitzerCard,
    } <= types


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


def test_bill_noface_draws_extra():
    gm = GameManager()
    bn = Player("Bill", character=BillNoface())
    gm.add_player(bn)
    bn.health -= 2
    gm.draw_phase(bn)
    assert len(bn.hand) == 3


def test_belle_star_ignores_barrel():
    gm = GameManager()
    belle = Player("Belle", character=BelleStar())
    target = Player("T")
    gm.add_player(belle)
    gm.add_player(target)
    BarrelCard().play(target)
    belle.hand.append(BangCard())
    gm.play_card(belle, belle.hand[0], target)
    assert target.health == target.max_health - 1


def test_chuck_wengam_ability():
    gm = GameManager()
    chuck = Player("Chuck", character=ChuckWengam())
    gm.add_player(chuck)
    gm.chuck_wengam_ability(chuck)
    assert chuck.health == chuck.max_health - 1
    assert len(chuck.hand) == 2


def test_doc_holyday_free_bang():
    gm = GameManager()
    doc = Player("Doc", character=DocHolyday())
    target = Player("T")
    gm.add_player(doc)
    gm.add_player(target)
    doc.hand.extend([PanicCard(), PanicCard()])
    gm.doc_holyday_ability(doc, [0, 1])
    bang = next(c for c in doc.hand if isinstance(c, BangCard))
    gm.play_card(doc, bang, target)
    assert doc.metadata.bangs_played == 0


def test_elena_fuente_any_card_as_missed():
    gm = GameManager()
    attacker = Player("A")
    elena = Player("Elena", character=ElenaFuente())
    gm.add_player(attacker)
    gm.add_player(elena)
    elena.hand.append(PanicCard())
    attacker.hand.append(BangCard())
    gm.play_card(attacker, attacker.hand[0], elena)
    assert elena.health == elena.max_health


def test_molly_stark_draws_when_discarding():
    gm = GameManager()
    molly = Player("Molly", character=MollyStark())
    attacker = Player("A")
    gm.add_player(molly)
    gm.add_player(attacker)
    molly.hand.append(BangCard())
    ind = IndiansCard()
    attacker.hand.append(ind)
    gm.play_card(attacker, ind, None)
    assert len(molly.hand) == 1


def test_molly_stark_draws_when_cat_baloued():
    gm = GameManager()
    molly = Player("Molly", character=MollyStark())
    attacker = Player("A")
    gm.add_player(molly)
    gm.add_player(attacker)
    molly.hand.append(BangCard())
    CatBalouCard().play(molly, game=gm)
    assert len(molly.hand) == 1


def test_molly_stark_draws_when_panicked():
    gm = GameManager()
    molly = Player("Molly", character=MollyStark())
    attacker = Player("A")
    gm.add_player(attacker)
    gm.add_player(molly)
    molly.hand.append(BeerCard())
    panic = PanicCard()
    attacker.hand.append(panic)
    gm.play_card(attacker, panic, molly)
    assert len(molly.hand) == 1


def test_pat_brennan_draw_in_play():
    gm = GameManager()
    pat = Player("Pat", character=PatBrennan())
    other = Player("O")
    gm.add_player(pat)
    gm.add_player(other)
    BarrelCard().play(other)
    gm.draw_phase(pat, pat_target=other, pat_card="Barrel")
    assert any("Barrel" in c.card_name for c in pat.hand)


def test_uncle_will_general_store():
    gm = GameManager()
    uw = Player("Will", character=UncleWill())
    other = Player("O")
    gm.add_player(uw)
    gm.add_player(other)
    uw.hand.append(PanicCard())
    gm.uncle_will_ability(uw, uw.hand[0])
    assert len(uw.hand) == 1


def test_johnny_kisch_discards_duplicates():
    gm = GameManager()
    johnny = Player("Johnny", character=JohnnyKisch())
    other = Player("O")
    gm.add_player(johnny)
    gm.add_player(other)
    BarrelCard().play(other)
    johnny.hand.append(BarrelCard())
    gm.play_card(johnny, johnny.hand[0], johnny)
    assert "Barrel" not in other.equipment


def test_claus_the_saint_distributes_cards():
    gm = GameManager()
    claus = Player("Claus", character=ClausTheSaint())
    p2 = Player("P2")
    p3 = Player("P3")
    gm.add_player(claus)
    gm.add_player(p2)
    gm.add_player(p3)
    gm.draw_phase(claus)
    assert len(claus.hand) == 2
    assert len(p2.hand) == 1
    assert len(p3.hand) == 1


def test_bullet_characters_instantiable():
    from bang_py.characters import (
        BelleStar,
        BillNoface,
        ChuckWengam,
        DocHolyday,
        ElenaFuente,
        HerbHunter,
        MollyStark,
        PatBrennan,
        UncleWill,
        JohnnyKisch,
        ClausTheSaint,
    )

    chars = [
        BelleStar,
        BillNoface,
        ChuckWengam,
        DocHolyday,
        ElenaFuente,
        HerbHunter,
        MollyStark,
        PatBrennan,
        UncleWill,
        JohnnyKisch,
        ClausTheSaint,
    ]

    instances = [cls() for cls in chars]
    assert len(instances) == len(chars)




def test_high_noon_event_deck_draw():
    gm = GameManager(expansions=["high_noon"])
    sheriff = Player("Sheriff", role=Role.SHERIFF)
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.start_game()
    assert gm.current_event is not None


def test_pepperbox_activates_after_turn():
    gm = GameManager()
    p1 = Player("Shooter")
    p2 = Player("Other")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.start_game()
    card = PepperboxCard()
    p1.hand.append(card)
    gm.play_card(p1, card, p1)
    assert p1.attack_range == 1
    gm.end_turn()
    assert p1.attack_range == 3


def test_binoculars_and_hideout_activate_after_turn():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.start_game()
    b = BinocularsCard()
    h = HideoutCard()
    p1.hand.extend([b, h])
    gm.play_card(p1, b, p1)
    gm.play_card(p1, h, p1)
    assert p1.attack_range == 1
    assert p2.distance_to(p1) == 1
    gm.end_turn()
    assert p1.attack_range == 2
    assert p2.distance_to(p1) == 2


def test_howitzer_hits_all_opponents():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    card = HowitzerCard()
    p1.hand.append(card)
    gm.play_card(p1, card)
    assert p2.health == p2.max_health - 1
    assert p3.health == p3.max_health - 1
