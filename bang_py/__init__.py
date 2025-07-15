"""Bang card game modules"""

from .game_manager import GameManager
from .deck_factory import create_standard_deck
from .player import Player, Role, PlayerMetadata
from .characters.base import BaseCharacter
from .characters.bart_cassidy import BartCassidy
from .characters.black_jack import BlackJack
from .characters.calamity_janet import CalamityJanet
from .characters.el_gringo import ElGringo
from .characters.jesse_jones import JesseJones
from .characters.jourdonnais import Jourdonnais
from .characters.kit_carlson import KitCarlson
from .characters.lucky_duke import LuckyDuke
from .characters.paul_regret import PaulRegret
from .characters.pedro_ramirez import PedroRamirez
from .characters.rose_doolan import RoseDoolan
from .characters.sid_ketchum import SidKetchum
from .characters.slab_the_killer import SlabTheKiller
from .characters.suzy_lafayette import SuzyLafayette
from .characters.vulture_sam import VultureSam
from .characters.willy_the_kid import WillyTheKid

__all__ = [
    "GameManager",
    "Player",
    "Role",
    "PlayerMetadata",
    "BaseCharacter",
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
