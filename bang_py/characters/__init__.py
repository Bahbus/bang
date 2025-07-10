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
        "During your draw phase, reveal the second card. If it's Heart or Diamond, draw one additional card."
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
        "At the start of your draw phase, you may draw the first card from another player's hand instead of the deck."
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
        "At the start of your draw phase, you may take the top card from the discard pile instead of drawing."
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
]
