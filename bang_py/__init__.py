"""Bang card game modules"""

from .game_manager import GameManager
from .player import Player, Role

__all__ = ["GameManager", "Player", "Role"]
try:
    from .network.server import BangServer
except Exception:  # Server requires optional websockets dependency
    BangServer = None
else:
    __all__.append("BangServer")
