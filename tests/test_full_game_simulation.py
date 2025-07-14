import random
from typing import List

from bang_py.game_manager import GameManager
from bang_py.player import Player, Role
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
from bang_py.cards import (
    BangCard,
    BeerCard,
    StagecoachCard,
    WellsFargoCard,
    CatBalouCard,
    PanicCard,
    IndiansCard,
    DuelCard,
    GeneralStoreCard,
    SaloonCard,
    GatlingCard,
)

CHAR_CLASSES = [
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

ROLE_MAP = {
    4: [Role.SHERIFF, Role.RENEGADE, Role.OUTLAW, Role.OUTLAW],
    5: [Role.SHERIFF, Role.RENEGADE, Role.DEPUTY, Role.OUTLAW, Role.OUTLAW],
    6: [
        Role.SHERIFF,
        Role.RENEGADE,
        Role.DEPUTY,
        Role.OUTLAW,
        Role.OUTLAW,
        Role.OUTLAW,
    ],
    7: [
        Role.SHERIFF,
        Role.RENEGADE,
        Role.DEPUTY,
        Role.DEPUTY,
        Role.OUTLAW,
        Role.OUTLAW,
        Role.OUTLAW,
    ],
}


def choose_target(player: Player, gm: GameManager, max_dist: int | None = None) -> Player | None:
    targets = [p for p in gm.players if p is not player and p.is_alive()]
    if max_dist is not None:
        targets = [t for t in targets if player.distance_to(t) <= max_dist]
    else:
        targets = [t for t in targets if player.distance_to(t) <= player.attack_range]
    return random.choice(targets) if targets else None


def auto_turn(gm: GameManager) -> None:
    if not gm.turn_order:
        return
    idx = gm.turn_order[gm.current_turn]
    player = gm.players[idx]
    if not player.is_alive():
        if gm.turn_order:
            gm.current_turn %= len(gm.turn_order)
            gm.end_turn()
        return
    played = True
    while played:
        played = False
        for card in list(player.hand):
            if not player.is_alive():
                break
            if card.card_type in {"equipment", "green"} and card.card_name != "Jail":
                gm.play_card(player, card, player)
                played = True
                break
            if isinstance(card, (StagecoachCard, WellsFargoCard, GeneralStoreCard, SaloonCard)):
                gm.play_card(player, card)
                played = True
                break
            if isinstance(card, BeerCard):
                alive = [p for p in gm.players if p.is_alive()]
                if player.health < player.max_health and len(alive) > 2:
                    gm.play_card(player, card, player)
                    played = True
                    break
            if isinstance(card, (GatlingCard, IndiansCard)):
                gm.play_card(player, card)
                played = True
                break
            if isinstance(card, CatBalouCard):
                target = choose_target(player, gm, max_dist=player.attack_range)
                if target:
                    gm.play_card(player, card, target)
                    played = True
                    break
            if isinstance(card, PanicCard):
                target = choose_target(player, gm, max_dist=1)
                if target:
                    gm.play_card(player, card, target)
                    played = True
                    break
            if isinstance(card, DuelCard):
                target = choose_target(player, gm)
                if target:
                    gm.play_card(player, card, target)
                    played = True
                    break
            if isinstance(card, BangCard):
                bangs = player.metadata.bangs_played
                unlimited = isinstance(player.character, WillyTheKid)
                if bangs >= 1 and not unlimited:
                    continue
                target = choose_target(player, gm)
                if target:
                    gm.play_card(player, card, target)
                    played = True
                    break
    if gm.turn_order and player.is_alive():
        gm.current_turn %= len(gm.turn_order)
        gm.end_turn()


def simulate_game(num_players: int) -> str:
    random.seed(100 + num_players)
    gm = GameManager()
    roles = ROLE_MAP[num_players][:]
    random.shuffle(roles)
    chars = CHAR_CLASSES[:]
    random.shuffle(chars)
    for i in range(num_players):
        player = Player(f"P{i}", role=roles[i], character=chars[i]())
        gm.add_player(player)
    result: List[str] = []

    def _record_result(res: str) -> None:
        result.append(res)

    gm.game_over_listeners.append(_record_result)
    gm.start_game()
    steps = 0
    while not result and steps < 2000:
        auto_turn(gm)
        steps += 1
    assert result, "Game did not finish"
    return result[0]


def test_full_game_simulation() -> None:
    for n in range(4, 8):
        outcome = simulate_game(n)
        assert "win" in outcome
