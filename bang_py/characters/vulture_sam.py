"""Claim all cards from eliminated players. Core set."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol
    from ..player import Player


class VultureSam(BaseCharacter):
    name = "Vulture Sam"
    description = "Whenever another player is eliminated, take all the cards from his hand."
    starting_health = 4

    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(VultureSam)

        def on_death(victim: "Player", _src: "Player | None") -> None:
            if victim is not player:
                player.hand.extend(victim.hand)
                victim.hand.clear()

        gm.player_death_listeners.append(on_death)
        return True
