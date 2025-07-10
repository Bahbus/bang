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
