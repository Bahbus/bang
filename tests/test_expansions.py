from bang_py.deck_factory import create_standard_deck
from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard
from bang_py.deck import Deck
from bang_py.cards import (
    PunchCard,
    HideoutCard,
    BinocularsCard,
    BuffaloRifleCard,
    PepperboxCard,
    HowitzerCard,
    MissedCard,
    KnifeCard,
    BrawlCard,
    SpringfieldCard,
    WhiskyCard,
    HighNoonCard,
    PonyExpressCard,
    TequilaCard,
    RagTimeCard,
    BibleCard,
    CanteenCard,
    ConestogaCard,
    CanCanCard,
    TenGallonHatCard,
    BeerCard,
    BarrelCard,
    BangCard,
    CatBalouCard,
    PanicCard,
    IndiansCard,
    DuelCard,
)
from bang_py.characters.bill_noface import BillNoface
from bang_py.characters.belle_star import BelleStar
from bang_py.characters.chuck_wengam import ChuckWengam
from bang_py.characters.claus_the_saint import ClausTheSaint
from bang_py.characters.doc_holyday import DocHolyday
from bang_py.characters.elena_fuente import ElenaFuente
from bang_py.characters.johnny_kisch import JohnnyKisch
from bang_py.characters.molly_stark import MollyStark
from bang_py.characters.pat_brennan import PatBrennan
from bang_py.characters.pixie_pete import PixiePete
from bang_py.characters.sean_mallory import SeanMallory
from bang_py.characters.tequila_joe import TequilaJoe
from bang_py.characters.uncle_will import UncleWill


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
    deck = Deck([BangCard(), BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p1 = Player("A")
    gm.add_player(p1)
    card = WhiskyCard()
    p1.health = p1.max_health - 2
    p1.hand.extend([BangCard(), card])
    gm.play_card(p1, card, p1)
    assert p1.health == p1.max_health
    assert not p1.hand


def test_high_noon_draws_card_for_all():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.deck.cards.extendleft([PunchCard(), PunchCard()])
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


def test_rag_time_steals_card():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    card = RagTimeCard()
    p1.hand.extend([BangCard(), card])
    stolen = BangCard()
    p2.hand.append(stolen)
    gm.play_card(p1, card, p2)
    assert stolen in p1.hand
    assert not p2.hand


def test_tequila_heals_one():
    gm = GameManager()
    p1 = Player("A")
    gm.add_player(p1)
    card = TequilaCard()
    p1.hand.extend([BangCard(), card])
    p1.health -= 1
    gm.play_card(p1, card, p1)
    assert p1.health == p1.max_health
    assert not p1.hand


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
    for cb in gm.turn_started_listeners:
        cb(belle)
    gm.play_card(belle, belle.hand[0], target)
    assert target.health == target.max_health - 1


def test_belle_star_ignores_barrel_on_green():
    gm = GameManager()
    belle = Player("Belle", character=BelleStar())
    target = Player("T")
    gm.add_player(belle)
    gm.add_player(target)
    BarrelCard().play(target)
    pepper = PepperboxCard()
    belle.hand.append(pepper)
    for cb in gm.turn_started_listeners:
        cb(belle)
    gm.play_card(belle, pepper, target)
    assert target.health == target.max_health - 1


def test_chuck_wengam_ability():
    gm = GameManager()
    chuck = Player("Chuck", character=ChuckWengam())
    gm.add_player(chuck)
    chuck.character.use_ability(gm, chuck)
    assert chuck.health == chuck.max_health - 1
    assert len(chuck.hand) == 2


def test_doc_holyday_free_bang():
    gm = GameManager()
    doc = Player("Doc", character=DocHolyday())
    target = Player("T")
    gm.add_player(doc)
    gm.add_player(target)
    doc.hand.extend([PanicCard(), PanicCard()])
    doc.character.use_ability(gm, doc, [0, 1])
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


def test_molly_stark_draws_after_duel():
    deck = Deck([BangCard()])
    gm = GameManager(deck=deck)
    molly = Player("Molly", character=MollyStark())
    attacker = Player("A")
    gm.add_player(molly)
    gm.add_player(attacker)
    molly.hand.append(BangCard())
    duel = DuelCard()
    attacker.hand.append(duel)
    gm.play_card(attacker, duel, molly)
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
    uw.character.use_ability(gm, uw, uw.hand[0])
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


def test_johnny_kisch_discards_green_equipment():
    gm = GameManager()
    johnny = Player("Johnny", character=JohnnyKisch())
    other = Player("O")
    gm.add_player(johnny)
    gm.add_player(other)
    BinocularsCard().play(other)
    johnny.hand.append(BinocularsCard())
    gm.play_card(johnny, johnny.hand[0], johnny)
    assert "Binoculars" not in other.equipment


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
    from bang_py.characters.belle_star import BelleStar
    from bang_py.characters.bill_noface import BillNoface
    from bang_py.characters.chuck_wengam import ChuckWengam
    from bang_py.characters.doc_holyday import DocHolyday
    from bang_py.characters.elena_fuente import ElenaFuente
    from bang_py.characters.herb_hunter import HerbHunter
    from bang_py.characters.molly_stark import MollyStark
    from bang_py.characters.pat_brennan import PatBrennan
    from bang_py.characters.uncle_will import UncleWill
    from bang_py.characters.johnny_kisch import JohnnyKisch
    from bang_py.characters.claus_the_saint import ClausTheSaint

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
    sheriff = Player("Sheriff", role=SheriffRoleCard())
    outlaw = Player("Outlaw")
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    gm.start_game(deal_roles=False)
    assert gm.current_event is None
    gm.end_turn()
    gm.end_turn()
    assert gm.current_event is not None


def test_pepperbox_acts_as_bang():
    deck = Deck([BangCard(), BangCard(), BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p1 = Player("Shooter")
    p2 = Player("Target")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.start_game(deal_roles=False)
    card = PepperboxCard()
    p1.hand.append(card)
    gm.play_card(p1, card, p2)
    assert p2.health == p2.max_health - 1


def test_binoculars_and_hideout_activate_after_turn():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.start_game(deal_roles=False)
    b = BinocularsCard()
    h = HideoutCard()
    p1.hand.extend([b, h])
    gm.play_card(p1, b, p1)
    gm.play_card(p1, h, p1)
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


def test_knife_can_be_dodged():
    gm = GameManager()
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    card = KnifeCard()
    attacker.hand.append(card)
    target.hand.append(MissedCard())
    gm.play_card(attacker, card, target)
    assert target.health == target.max_health
    assert not target.hand


def test_brawl_discards_adjacent():
    gm = GameManager()
    a = Player("A")
    b = Player("B")
    c = Player("C")
    gm.add_player(a)
    gm.add_player(b)
    gm.add_player(c)
    b.hand.append(BangCard())
    c.hand.append(BangCard())
    card = BrawlCard()
    a.hand.extend([BangCard(), card])
    gm.play_card(a, card, a)
    assert not b.hand
    assert not c.hand
    assert not a.hand


def test_springfield_long_range():
    gm = GameManager()
    a = Player("A")
    b = Player("B")
    c = Player("C")
    d = Player("D")
    gm.add_player(a)
    gm.add_player(b)
    gm.add_player(c)
    gm.add_player(d)
    card = SpringfieldCard()
    a.hand.extend([BangCard(), card])
    c.hand.append(MissedCard())
    gm.play_card(a, card, c)
    assert c.health == c.max_health
    assert not c.hand
    assert not a.hand


def test_green_bordered_cards():
    import inspect
    from bang_py import cards as card_mod

    allowed = {
        "BibleCard",
        "BuffaloRifleCard",
        "CanCanCard",
        "CanteenCard",
        "ConestogaCard",
        "DerringerCard",
        "HowitzerCard",
        "IronPlateCard",
        "KnifeCard",
        "PepperboxCard",
        "PonyExpressCard",
        "SombreroCard",
        "TenGallonHatCard",
    }
    green = {
        name
        for name, obj in inspect.getmembers(card_mod, inspect.isclass)
        if getattr(obj, "card_type", "") == "green"
    }
    assert green <= allowed


def test_bible_card_dodges_and_draws():
    gm = GameManager()
    p = Player("P")
    gm.add_player(p)
    card = BibleCard()
    p.hand.append(card)
    gm.play_card(p, card, p)
    assert p.metadata.dodged is True
    assert len(p.hand) == 1


def test_canteen_card_heals():
    gm = GameManager()
    p = Player("P")
    gm.add_player(p)
    p.health -= 1
    card = CanteenCard()
    p.hand.append(card)
    gm.play_card(p, card, p)
    assert p.health == p.max_health


def test_conestoga_steals_card():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    stolen = BangCard()
    p2.hand.append(stolen)
    card = ConestogaCard()
    p1.hand.append(card)
    gm.play_card(p1, card, p2)
    assert stolen in p1.hand
    assert not p2.hand


def test_can_can_discards_card():
    gm = GameManager()
    attacker = Player("A")
    target = Player("B")
    gm.add_player(attacker)
    gm.add_player(target)
    target.hand.append(BangCard())
    card = CanCanCard()
    attacker.hand.append(card)
    gm.play_card(attacker, card, target)
    assert not target.hand


def test_ten_gallon_hat_is_missed():
    target = Player("T")
    TenGallonHatCard().play(target)
    assert target.metadata.dodged is True
