"""Draw two cards when someone else is eliminated. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol
    from ..player import Player


class HerbHunter(BaseCharacter):
    name = "Herb Hunter"
    description = "Whenever another player is eliminated, draw two extra cards."
    starting_health = 4

    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(HerbHunter)

        def on_death(victim: "Player", _src: "Player | None") -> None:
            if victim is not player:
                gm.draw_card(player, 2)

        gm.player_death_listeners.append(on_death)
        return True
