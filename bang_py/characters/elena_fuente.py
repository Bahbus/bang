from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class ElenaFuente(BaseCharacter):
    name = "Elena Fuente"
    description = "You may play any card from your hand as a Missed!."
    starting_health = 3

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(ElenaFuente)
        player.metadata.any_card_as_missed = True
        return True
