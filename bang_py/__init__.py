"""Bang card game modules"""

from .game_manager import GameManager
from .deck_factory import create_standard_deck
from .player import Player, Role
from .characters import (
    Character,
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

__all__ = [
    "GameManager",
    "Player",
    "Role",
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
    "create_standard_deck",
]
try:
    from .network.server import BangServer
except Exception:  # Server requires optional websockets dependency
    BangServer = None
else:
    __all__.append("BangServer")
