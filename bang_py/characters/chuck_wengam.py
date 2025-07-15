from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player

class ChuckWengam(BaseCharacter):
    name = "Chuck Wengam"
    description = (
        "During your turn, you may lose 1 life point to draw 2 cards."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(ChuckWengam)
        return True

    def use_ability(self, gm: "GameManager", player: "Player") -> bool:
        if player.health <= 1:
            return True
        player.take_damage(1)
        gm.on_player_damaged(player)
        gm.draw_card(player, 2)
        return True
