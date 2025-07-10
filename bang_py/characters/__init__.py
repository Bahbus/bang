class Character:
    """Base class for Bang characters."""

    name: str = "Character"
    description: str = ""
    range_modifier: int = 0
    distance_modifier: int = 0
    max_health_modifier: int = 0


class BartCassidy(Character):
    name = "Bart Cassidy"
    description = (
        "When you lose a life point, draw a card from the deck."
    )


class BlackJack(Character):
    name = "Black Jack"
    description = (
        "During your draw phase, reveal the second card. "
        "If it's Heart or Diamond, draw one additional card."
    )


class CalamityJanet(Character):
    name = "Calamity Janet"
    description = "You may play Bang! cards as Missed! and vice versa."


class ElGringo(Character):
    name = "El Gringo"
    description = (
        "When you lose a life point, draw a random card from the player who caused the damage."
    )


class JesseJones(Character):
    name = "Jesse Jones"
    description = (
        "At the start of your draw phase, you may draw the first card from another "
        "player's hand instead of the deck."
    )


class Jourdonnais(Character):
    name = "Jourdonnais"
    description = "You are considered to have a Barrel in play at all times."


class KitCarlson(Character):
    name = "Kit Carlson"
    description = (
        "During your draw phase, draw one extra card, choose two and discard the third."
    )


class LuckyDuke(Character):
    name = "Lucky Duke"
    description = (
        "Whenever you must draw! you flip two cards and choose the result you prefer."
    )


class PaulRegret(Character):
    name = "Paul Regret"
    description = "Players see you at distance +1."
    distance_modifier = 1


class PedroRamirez(Character):
    name = "Pedro Ramirez"
    description = (
        "At the start of your draw phase, you may take the top card from the discard "
        "pile instead of drawing."
    )


class RoseDoolan(Character):
    name = "Rose Doolan"
    description = "You see all players at a distance -1."
    range_modifier = 1


class SidKetchum(Character):
    name = "Sid Ketchum"
    description = "You may discard two cards to regain one life point."


class SlabTheKiller(Character):
    name = "Slab the Killer"
    description = "Players need two Missed! cards to cancel your Bang!."


class SuzyLafayette(Character):
    name = "Suzy Lafayette"
    description = "As soon as you have no cards in hand, draw a card."


class VultureSam(Character):
    name = "Vulture Sam"
    description = (
        "Whenever another player is eliminated, take all the cards from his hand."
    )


class WillyTheKid(Character):
    name = "Willy the Kid"
    description = "You may play any number of Bang! cards during your turn."


class PixiePete(Character):
    name = "Pixie Pete"
    description = "During your draw phase, draw three cards instead of two."


class JoseDelgado(Character):
    name = "Jose Delgado"
    description = "You may discard an equipment card to draw two cards."


class SeanMallory(Character):
    name = "Sean Mallory"
    description = "You have no limit to the number of cards in hand."


class TequilaJoe(Character):
    name = "Tequila Joe"
    description = "Beer cards heal you by 2 life points."


class VeraCuster(Character):
    name = "Vera Custer"
    description = "At the start of your turn, copy another living character's ability."


class ApacheKid(Character):
    name = "Apache Kid"
    description = "You are unaffected by Diamond suited cards."


class GregDigger(Character):
    name = "Greg Digger"
    description = "Each time a player is eliminated, regain two life points."


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
]
