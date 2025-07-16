from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class ElGringo(BaseCharacter):
    name = "El Gringo"
    description = (
        "When you lose a life point, take a card of your choice (blindly) from the player"
        " who caused the damage."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(ElGringo)


        def on_damaged(p: "Player", src: "Player | None", *__: object) -> None:
            if p is player and src and src.hand:
                idx = player.metadata.gringo_index or 0
                if idx < 0 or idx >= len(src.hand):
                    idx = 0
                stolen = src.hand.pop(idx)
                player.hand.append(stolen)
                player.metadata.gringo_index = None

        gm.player_damaged_listeners.append(on_damaged)
        return True
