from bang_py.player import Player
from bang_py.cards.scope import ScopeCard
from bang_py.characters.bart_cassidy import BartCassidy
from bang_py.characters.black_jack import BlackJack
from bang_py.characters.calamity_janet import CalamityJanet
from bang_py.characters.el_gringo import ElGringo
from bang_py.characters.jesse_jones import JesseJones
from bang_py.characters.jourdonnais import Jourdonnais
from bang_py.characters.kit_carlson import KitCarlson
from bang_py.characters.lucky_duke import LuckyDuke
from bang_py.characters.jose_delgado import JoseDelgado
from bang_py.characters.paul_regret import PaulRegret
from bang_py.characters.pedro_ramirez import PedroRamirez
from bang_py.characters.rose_doolan import RoseDoolan
from bang_py.characters.sid_ketchum import SidKetchum
from bang_py.characters.slab_the_killer import SlabTheKiller
from bang_py.characters.suzy_lafayette import SuzyLafayette
from bang_py.characters.vulture_sam import VultureSam
from bang_py.characters.willy_the_kid import WillyTheKid
from bang_py.characters.apache_kid import ApacheKid
from bang_py.characters.sean_mallory import SeanMallory
from bang_py.game_manager import GameManager
from bang_py.deck_factory import create_standard_deck
from bang_py.deck import Deck
from bang_py.cards.bang import BangCard
from bang_py.cards.beer import BeerCard
from bang_py.cards.missed import MissedCard
from bang_py.cards.jail import JailCard
from bang_py.cards.duel import DuelCard
from bang_py.cards.barrel import BarrelCard


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


def test_character_ability_registered():
    gm = GameManager()
    player = Player("Kid", character=ApacheKid())
    gm.add_player(player)
    assert ApacheKid in player.metadata.abilities


def test_bart_cassidy_draw_on_damage():
    deck = create_standard_deck()
    deck.push_top(BangCard())
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
    deck.extend_top(
        [
            BeerCard(suit="Clubs"),
            BeerCard(suit="Diamonds"),
            BeerCard(suit="Spades"),
        ]
    )
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


def test_calamity_janet_dodges_with_bang():
    gm = GameManager()
    attacker = Player("Bandit")
    janet = Player("Janet", character=CalamityJanet())
    gm.add_player(attacker)
    gm.add_player(janet)
    janet.hand.append(BangCard())
    attacker.hand.append(BangCard())
    gm.play_card(attacker, attacker.hand[0], janet)
    assert janet.health == janet.max_health
    assert janet.metadata.dodged is True
    assert len(janet.hand) == 0
    assert sum(isinstance(c, BangCard) for c in gm.discard_pile) == 2


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
    deck.push_top(BangCard())
    gm = GameManager(deck=deck)
    jj = Player("JJ", character=JesseJones())
    other = Player("Other")
    other.hand.append(BangCard())
    gm.add_player(jj)
    gm.add_player(other)
    gm.draw_phase(jj, jesse_target=other)
    assert len(jj.hand) == 2
    assert len(other.hand) == 0


def test_jesse_jones_selects_card_index():
    deck = create_standard_deck()
    deck.push_top(BangCard())
    gm = GameManager(deck=deck)
    jj = Player("JJ", character=JesseJones())
    other = Player("Other")
    other.hand.extend([BangCard(), BeerCard()])
    gm.add_player(jj)
    gm.add_player(other)
    gm.draw_phase(jj, jesse_target=other, jesse_card=1)
    assert len(jj.hand) == 2
    assert len(other.hand) == 1
    assert isinstance(other.hand[0], BangCard)


def test_jourdonnais_has_virtual_barrel():
    deck = create_standard_deck()
    deck.push_top(BeerCard(suit="Hearts"))
    gm = GameManager(deck=deck)
    target = Player("Jour", character=Jourdonnais())
    gm.add_player(target)
    BangCard().play(target, game=gm)
    assert target.metadata.dodged is True


def test_kit_carlson_draw_three_keep_two():
    deck = create_standard_deck()
    deck.extend_top([BangCard(), BeerCard(), MissedCard()])
    gm = GameManager(deck=deck)
    kit = Player("Kit", character=KitCarlson())
    gm.add_player(kit)
    gm.draw_phase(kit, kit_back=1)
    assert len(kit.hand) == 2
    assert len(gm.discard_pile) == 0


def test_lucky_duke_draw_two_on_jail():
    deck = create_standard_deck()
    deck.extend_top([BangCard(suit="Clubs"), BangCard(suit="Hearts")])
    gm = GameManager(deck=deck)
    player = Player("Lucky", character=LuckyDuke())
    gm.add_player(player)
    jail = JailCard()
    jail.play(player)
    skipped = jail.check_turn(gm, player)
    assert skipped is False
    assert len(gm.discard_pile) == 2


def test_barrel_draw_card_discarded():
    deck = Deck([BangCard()])
    gm = GameManager(deck=deck)
    player = Player("T")
    gm.add_player(player)
    barrel = BarrelCard()
    barrel.play(player)
    assert barrel.draw_check(gm, player) is False
    assert len(gm.discard_pile) == 1


def test_pedro_ramirez_takes_from_discard():
    deck = create_standard_deck()
    deck.push_top(BangCard())
    gm = GameManager(deck=deck)
    gm.discard_pile.append(MissedCard())
    pedro = Player("Pedro", character=PedroRamirez())
    gm.add_player(pedro)
    gm.draw_phase(pedro, pedro_use_discard=True)
    assert len(pedro.hand) == 2


def test_pedro_ramirez_draws_from_deck_when_chosen():
    deck = create_standard_deck()
    deck.extend_top([BangCard(), BeerCard()])
    gm = GameManager(deck=deck)
    gm.discard_pile.append(MissedCard())
    pedro = Player("Pedro", character=PedroRamirez())
    gm.add_player(pedro)
    gm.draw_phase(pedro, pedro_use_discard=False)
    assert len(pedro.hand) == 2


def test_jose_delgado_discards_selected_equipment():
    deck = create_standard_deck()
    gm = GameManager(deck=deck)
    jose = Player("Jose", character=JoseDelgado())
    gm.add_player(jose)
    gun = BangCard()
    gun.slot = "Gun"
    barrel = MissedCard()
    barrel.slot = "Barrel"
    jose.hand.extend([gun, barrel])
    gm.draw_phase(jose, jose_equipment=1)
    assert len(gm.discard_pile) == 1
    assert gm.discard_pile[0] is barrel
    assert len(jose.hand) == 4
    assert gun in jose.hand and barrel not in jose.hand


def test_sid_ketchum_discard_two_to_heal():
    gm = GameManager()
    sid = Player("Sid", character=SidKetchum())
    gm.add_player(sid)
    sid.hand.extend([BangCard(), BeerCard()])
    sid.health -= 1
    sid.character.use_ability(gm, sid, [0, 1])
    assert sid.health == sid.max_health
    assert len(sid.hand) == 0


def test_suzy_lafayette_draws_when_empty():
    deck = create_standard_deck()
    deck.push_top(BangCard())
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


def test_slab_the_killer_requires_two_missed():
    gm = GameManager()
    slab = Player("Slab", character=SlabTheKiller())
    target = Player("Target")
    gm.add_player(slab)
    gm.add_player(target)
    target.hand.extend([MissedCard(), MissedCard()])
    slab.hand.append(BangCard())
    gm.play_card(slab, slab.hand[0], target)
    assert target.health == target.max_health
    assert len(target.hand) == 0


def test_slab_the_killer_bang_hits_without_two_missed():
    gm = GameManager()
    slab = Player("Slab", character=SlabTheKiller())
    target = Player("Target")
    gm.add_player(slab)
    gm.add_player(target)
    target.hand.append(MissedCard())
    slab.hand.append(BangCard())
    gm.play_card(slab, slab.hand[0], target)
    assert target.health == target.max_health - 1
    assert len(target.hand) == 1


def test_apache_kid_ignores_diamond_bang():
    gm = GameManager()
    kid = Player("Kid", character=ApacheKid())
    att = Player("A")
    gm.add_player(kid)
    gm.add_player(att)
    bang = BangCard(suit="Diamonds")
    att.hand.append(bang)
    gm.play_card(att, bang, kid)
    assert kid.health == kid.max_health


def test_apache_kid_cancels_diamond_duel():
    gm = GameManager()
    kid = Player("Kid", character=ApacheKid())
    att = Player("A")
    gm.add_player(kid)
    gm.add_player(att)
    duel = DuelCard(suit="Diamonds")
    att.hand.append(duel)
    gm.play_card(att, duel, kid)
    assert kid.health == kid.max_health


def test_sean_mallory_hand_limit_ten():
    gm = GameManager()
    sean = Player("Sean", character=SeanMallory())
    gm.add_player(sean)
    for _ in range(12):
        sean.hand.append(BangCard())
    gm.discard_phase(sean)
    assert len(sean.hand) == 10
