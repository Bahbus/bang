from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player

class SidKetchum(BaseCharacter):
    name = "Sid Ketchum"
    description = "You may discard two cards to regain one life point."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(SidKetchum)
        return True

    def use_ability(
        self,
        gm: "GameManager",
        player: "Player",
        indices: list[int] | None = None,
    ) -> bool:
        if len(player.hand) < 2 or player.health >= player.max_health:
            return True
        discard_indices = sorted(indices or list(range(2)), reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                gm._pass_left_or_discard(player, card)
        player.heal(1)
        gm.on_player_healed(player)
        return True
