from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class Character:
    """Base class for Bang characters."""

    name: str = "Character"
    description: str = ""
    range_modifier: int = 0
    distance_modifier: int = 0
    starting_health: int = 4

    def draw_phase(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        """Handle draw phase effects. Return ``True`` if handled."""
        return False


class BartCassidy(Character):
    name = "Bart Cassidy"
    description = (
        "When you lose a life point, draw a card from the deck."
    )
    starting_health = 4


class BlackJack(Character):
    name = "Black Jack"
    description = (
        "During your draw phase, reveal the second card. "
        "If it's Heart or Diamond, draw one additional card."
    )
    starting_health = 4

    def draw_phase(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        first = gm.deck.draw()
        if first:
            player.hand.append(first)
        second = gm.deck.draw()
        if second:
            player.hand.append(second)
            if getattr(second, "suit", None) in ("Hearts", "Diamonds"):
                gm.draw_card(player)
        return True


class CalamityJanet(Character):
    name = "Calamity Janet"
    description = "You may play Bang! cards as Missed! and vice versa."
    starting_health = 4


class ElGringo(Character):
    name = "El Gringo"
    description = (
        "When you lose a life point, draw a random card from the player who caused the damage."
    )
    starting_health = 4


class JesseJones(Character):
    name = "Jesse Jones"
    description = (
        "At the start of your draw phase, you may draw the first card from another "
        "player's hand instead of the deck."
    )
    starting_health = 4

    def draw_phase(
        self,
        gm: "GameManager",
        player: "Player",
        *,
        jesse_target: "Player | None" = None,
        **_: object,
    ) -> bool:
        opponents = [p for p in gm.players if p is not player and p.hand]
        if not opponents:
            return False
        source = jesse_target if jesse_target in opponents else random.choice(opponents)
        card = source.hand.pop()
        player.hand.append(card)
        gm.draw_card(player)
        return True


class Jourdonnais(Character):
    name = "Jourdonnais"
    description = "You are considered to have a Barrel in play at all times."
    starting_health = 4


class KitCarlson(Character):
    name = "Kit Carlson"
    description = (
        "During your draw phase, draw one extra card, choose two and discard the third."
    )
    starting_health = 4

    def draw_phase(
        self,
        gm: "GameManager",
        player: "Player",
        *,
        kit_discard: int | None = None,
        **_: object,
    ) -> bool:
        cards = [gm.deck.draw(), gm.deck.draw(), gm.deck.draw()]
        keep_cards = []
        for i, c in enumerate(cards):
            if c is None:
                continue
            if kit_discard is not None and i == kit_discard:
                gm.discard_pile.append(c)
            elif len(keep_cards) < 2:
                keep_cards.append(c)
            else:
                gm.discard_pile.append(c)
        for c in keep_cards:
            player.hand.append(c)
        return True


class LuckyDuke(Character):
    name = "Lucky Duke"
    description = (
        "Whenever you must draw! you flip two cards and choose the result you prefer."
    )
    starting_health = 4


class PaulRegret(Character):
    name = "Paul Regret"
    description = "Players see you at distance +1."
    distance_modifier = 1
    starting_health = 4


class PedroRamirez(Character):
    name = "Pedro Ramirez"
    description = (
        "At the start of your draw phase, you may take the top card from the discard "
        "pile instead of drawing."
    )
    starting_health = 4

    def draw_phase(
        self,
        gm: "GameManager",
        player: "Player",
        *,
        pedro_use_discard: bool | None = None,
        **_: object,
    ) -> bool:
        if not gm.discard_pile:
            return False
        if pedro_use_discard is False:
            gm.draw_card(player, 2)
        else:
            player.hand.append(gm.discard_pile.pop())
            gm.draw_card(player)
        return True


class RoseDoolan(Character):
    name = "Rose Doolan"
    description = "You see all players at a distance -1."
    range_modifier = 1
    starting_health = 4


class SidKetchum(Character):
    name = "Sid Ketchum"
    description = "You may discard two cards to regain one life point."
    starting_health = 4


class SlabTheKiller(Character):
    name = "Slab the Killer"
    description = "Players need two Missed! cards to cancel your Bang!."
    starting_health = 4


class SuzyLafayette(Character):
    name = "Suzy Lafayette"
    description = "As soon as you have no cards in hand, draw a card."
    starting_health = 4


class VultureSam(Character):
    name = "Vulture Sam"
    description = (
        "Whenever another player is eliminated, take all the cards from his hand."
    )
    starting_health = 4


class WillyTheKid(Character):
    name = "Willy the Kid"
    description = "You may play any number of Bang! cards during your turn."
    starting_health = 4


class PixiePete(Character):
    name = "Pixie Pete"
    description = "During your draw phase, draw three cards instead of two."
    starting_health = 4

    def draw_phase(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        gm.draw_card(player, 3)
        return True


class JoseDelgado(Character):
    name = "Jose Delgado"
    description = "You may discard an equipment card to draw two cards."
    starting_health = 4

    def draw_phase(
        self,
        gm: "GameManager",
        player: "Player",
        *,
        jose_equipment: int | None = None,
        **_: object,
    ) -> bool:
        equips = [c for c in player.hand if hasattr(c, "slot")]
        equip = None
        if jose_equipment is not None and 0 <= jose_equipment < len(equips):
            equip = equips[jose_equipment]
        elif equips:
            equip = equips[0]
        if equip:
            player.hand.remove(equip)
            gm.discard_pile.append(equip)
            gm.draw_card(player, 2)
        gm.draw_card(player)
        return True


class SeanMallory(Character):
    name = "Sean Mallory"
    description = "You have no limit to the number of cards in hand."
    starting_health = 4


class TequilaJoe(Character):
    name = "Tequila Joe"
    description = "Beer cards heal you by 2 life points."
    starting_health = 4


class VeraCuster(Character):
    name = "Vera Custer"
    description = "At the start of your turn, copy another living character's ability."
    starting_health = 4


class ApacheKid(Character):
    name = "Apache Kid"
    description = "You are unaffected by Diamond suited cards."
    starting_health = 4


class GregDigger(Character):
    name = "Greg Digger"
    description = "Each time a player is eliminated, regain two life points."
    starting_health = 4


class BelleStar(Character):
    name = "Belle Star"
    description = (
        "During your turn, cards in play in front of other players have no effect."
    )
    starting_health = 4


class BillNoface(Character):
    name = "Bill Noface"
    description = (
        "During phase 1 of your turn, draw 1 card plus 1 for each wound you have."
    )
    starting_health = 4

    def draw_phase(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        wounds = player.max_health - player.health
        gm.draw_card(player, 1 + wounds)
        return True


class ChuckWengam(Character):
    name = "Chuck Wengam"
    description = (
        "During your turn, you may lose 1 life point to draw 2 cards."
    )
    starting_health = 4


class DocHolyday(Character):
    name = "Doc Holyday"
    description = (
        "Once during your turn, discard any two cards for a Bang! that doesn't count toward your limit."
    )
    starting_health = 4


class ElenaFuente(Character):
    name = "Elena Fuente"
    description = "You may play any card from your hand as a Missed!."
    starting_health = 3


class HerbHunter(Character):
    name = "Herb Hunter"
    description = (
        "Whenever another player is eliminated, draw two extra cards."
    )
    starting_health = 4


class MollyStark(Character):
    name = "Molly Stark"
    description = (
        "Each time you play or discard a Missed!, Beer or Bang! out of turn, draw a card."
    )
    starting_health = 4


class PatBrennan(Character):
    name = "Pat Brennan"
    description = (
        "During phase 1 of your turn, you may draw a card in play instead of from the deck."
    )
    starting_health = 4

    def draw_phase(
        self,
        gm: "GameManager",
        player: "Player",
        *,
        pat_target: "Player | None" = None,
        pat_card: str | None = None,
        **_: object,
    ) -> bool:
        if not gm.pat_brennan_draw(player, pat_target, pat_card):
            gm.draw_card(player)
        gm.draw_card(player)
        return True


class UncleWill(Character):
    name = "Uncle Will"
    description = (
        "Once during your turn, you may play any card from your hand as a General Store."
    )
    starting_health = 4


class JohnnyKisch(Character):
    name = "Johnny Kisch"
    description = (
        "Each time you put a card into play, discard all other cards with the same name in play."
    )
    starting_health = 4


class ClausTheSaint(Character):
    name = "Claus the Saint"
    description = (
        "During your draw phase, draw one more card than the number of players, keep two, then give one to each other player."
    )
    starting_health = 3

    def draw_phase(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        alive = [p for p in gm.players if p.is_alive()]
        cards = []
        for _ in range(len(alive) + 1):
            card = gm.deck.draw()
            if card:
                cards.append(card)
        keep = cards[:2]
        for c in keep:
            player.hand.append(c)
        others = [p for p in alive if p is not player]
        idx = 2
        for p in others:
            if idx < len(cards):
                p.hand.append(cards[idx])
                idx += 1
        return True



__all__ = [
    "Character",
    "BartCassidy",
    "BlackJack",
    "CalamityJanet",
    "ElGringo",
    "JesseJones",
    "Jourdonnais",
    "KitCarlson",
    "LuckyDuke",
    "PaulRegret",
    "PedroRamirez",
    "RoseDoolan",
    "SidKetchum",
    "SlabTheKiller",
    "SuzyLafayette",
    "VultureSam",
    "WillyTheKid",
    "PixiePete",
    "JoseDelgado",
    "SeanMallory",
    "TequilaJoe",
    "VeraCuster",
    "ApacheKid",
    "GregDigger",
    "BelleStar",
    "BillNoface",
    "ChuckWengam",
    "DocHolyday",
    "ElenaFuente",
    "HerbHunter",
    "MollyStark",
    "PatBrennan",
    "UncleWill",
    "JohnnyKisch",
    "ClausTheSaint",
]
