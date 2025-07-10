from bang_py.player import Player
from bang_py.cards.scope import ScopeCard
from bang_py.characters import (
    BartCassidy,
    BlackJack,
    CalamityJanet,
    ElGringo,
    JesseJones,
    Jourdonnais,
    KitCarlson,
    LuckyDuke,
    PaulRegret,
    PedroRamirez,
    RoseDoolan,
    SidKetchum,
    SlabTheKiller,
    SuzyLafayette,
    VultureSam,
    WillyTheKid,
)
from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.deck_factory import create_standard_deck
from bang_py.cards.bang import BangCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.missed import MissedCard
from bang_py.cards.jail import JailCard


def test_rose_doolan_range_bonus():
    player = Player("Rose", character=RoseDoolan())
    assert player.attack_range == 2
    target = Player("Bob")
    assert player.distance_to(target) == 1


def test_paul_regret_distance_bonus():
    attacker = Player("Attacker")
    target = Player("Paul", character=PaulRegret())
    assert attacker.distance_to(target) == 2
    ScopeCard().play(attacker)
    assert attacker.distance_to(target) == 1


def test_all_character_classes_instantiable():
    chars = [
        BartCassidy,
        BlackJack,
        CalamityJanet,
        ElGringo,
        JesseJones,
        Jourdonnais,
        KitCarlson,
        LuckyDuke,
        PaulRegret,
        PedroRamirez,
        RoseDoolan,
        SidKetchum,
        SlabTheKiller,
        SuzyLafayette,
        VultureSam,
        WillyTheKid,
    ]
    instances = [cls() for cls in chars]
    assert len(instances) == 16


def test_bart_cassidy_draw_on_damage():
    deck = create_standard_deck()
    deck.cards.append(BangCard())
    gm = GameManager(deck=deck)
    p1 = Player("Bart", character=BartCassidy())
    p2 = Player("Shooter")
    gm.add_player(p1)
    gm.add_player(p2)
    p2.hand.append(BangCard())
    gm.play_card(p2, p2.hand[0], p1)
    assert len(p1.hand) == 1


def test_black_jack_extra_draw():
    deck = create_standard_deck()
    deck.cards.extend([
        BeerCard(suit="Clubs"),
        BeerCard(suit="Diamonds"),
        BeerCard(suit="Spades"),
    ])
    gm = GameManager(deck=deck)
    p = Player("BJ", character=BlackJack())
    gm.add_player(p)
    gm.draw_phase(p)
    assert len(p.hand) == 3


def test_calamity_janet_plays_missed_as_bang():
    gm = GameManager()
    attacker = Player("Janet", character=CalamityJanet())
    target = Player("Bob")
    gm.add_player(attacker)
    gm.add_player(target)
    attacker.hand.append(MissedCard())
    gm.play_card(attacker, attacker.hand[0], target)
    assert target.health == target.max_health - 1


def test_el_gringo_steals_on_damage():
    gm = GameManager()
    gringo = Player("Gringo", character=ElGringo())
    attacker = Player("Bandit")
    gm.add_player(gringo)
    gm.add_player(attacker)
    attacker.hand.extend([BangCard(), BangCard()])
    gm.play_card(attacker, attacker.hand[0], gringo)
    assert len(gringo.hand) == 1
    assert len(attacker.hand) == 0


def test_jesse_jones_draws_from_opponent():
    deck = create_standard_deck()
    deck.cards.append(BangCard())
    gm = GameManager(deck=deck)
    jj = Player("JJ", character=JesseJones())
    other = Player("Other")
    other.hand.append(BangCard())
    gm.add_player(jj)
    gm.add_player(other)
    gm.draw_phase(jj)
    assert len(jj.hand) == 2
    assert len(other.hand) == 0


def test_jourdonnais_has_virtual_barrel():
    deck = create_standard_deck()
    deck.cards.append(BeerCard(suit="Hearts"))
    target = Player("Jour", character=Jourdonnais())
    BangCard().play(target, deck)
    assert target.metadata.get("dodged") is True


def test_kit_carlson_draw_three_keep_two():
    deck = create_standard_deck()
    deck.cards.extend([BangCard(), BeerCard(), MissedCard()])
    gm = GameManager(deck=deck)
    kit = Player("Kit", character=KitCarlson())
    gm.add_player(kit)
    gm.draw_phase(kit)
    assert len(kit.hand) == 2
    assert len(gm.discard_pile) == 1


def test_lucky_duke_draw_two_on_jail():
    deck = create_standard_deck()
    deck.cards.extend([BangCard(suit="Clubs"), BangCard(suit="Hearts")])
    player = Player("Lucky", character=LuckyDuke())
    jail = JailCard()
    jail.play(player)
    skipped = jail.check_turn(player, deck)
    assert skipped is False


def test_pedro_ramirez_takes_from_discard():
    deck = create_standard_deck()
    deck.cards.append(BangCard())
    gm = GameManager(deck=deck)
    gm.discard_pile.append(MissedCard())
    pedro = Player("Pedro", character=PedroRamirez())
    gm.add_player(pedro)
    gm.draw_phase(pedro)
    assert len(pedro.hand) == 2


def test_sid_ketchum_discard_two_to_heal():
    gm = GameManager()
    sid = Player("Sid", character=SidKetchum())
    gm.add_player(sid)
    sid.hand.extend([BangCard(), BeerCard()])
    sid.health -= 1
    gm.sid_ketchum_ability(sid)
    assert sid.health == sid.max_health
    assert len(sid.hand) == 0


def test_suzy_lafayette_draws_when_empty():
    deck = create_standard_deck()
    deck.cards.append(BangCard())
    gm = GameManager(deck=deck)
    suzy = Player("Suzy", character=SuzyLafayette())
    target = Player("Target")
    gm.add_player(suzy)
    gm.add_player(target)
    suzy.hand.append(BangCard())
    gm.play_card(suzy, suzy.hand[0], target)
    assert len(suzy.hand) == 1


def test_vulture_sam_loots_on_death():
    gm = GameManager()
    sam = Player("Sam", character=VultureSam())
    victim = Player("Vic")
    attacker = Player("Att")
    gm.add_player(sam)
    gm.add_player(victim)
    gm.add_player(attacker)
    victim.hand.append(BangCard())
    victim.health = 1
    attacker.hand.append(BangCard())
    gm.play_card(attacker, attacker.hand[0], victim)
    assert not victim.is_alive()
    assert len(sam.hand) == 1


def test_willy_the_kid_can_play_multiple_bangs():
    gm = GameManager()
    willy = Player("Willy", character=WillyTheKid())
    target = Player("Target")
    gm.add_player(willy)
    gm.add_player(target)
    willy.hand.extend([BangCard(), BangCard()])
    gm.play_card(willy, willy.hand[0], target)
    gm.play_card(willy, willy.hand[0], target)
    assert len(willy.hand) == 0
