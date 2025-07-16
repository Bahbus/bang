from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class BartCassidy(BaseCharacter):
    name = "Bart Cassidy"
    description = (
        "When you lose a life point, draw a card from the deck."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(BartCassidy)

        def on_damaged(p: "Player", _src: "Player | None", *__: object) -> None:
            if p is player:
                gm.draw_card(player)

        gm.player_damaged_listeners.append(on_damaged)
        return True
