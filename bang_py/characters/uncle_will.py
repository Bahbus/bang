from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class UncleWill(BaseCharacter):
    name = "Uncle Will"
    description = (
        "Once during your turn, you may play any card from your hand as a General Store."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(UncleWill)
        return True

    def use_ability(
        self,
        gm: "GameManager",
        player: "Player",
        card,
    ) -> bool:
        if player.metadata.uncle_used or card not in player.hand:
            return True
        player.metadata.uncle_used = True
        from ..cards.general_store import GeneralStoreCard

        GeneralStoreCard().play(player, player, game=gm)
        player.hand.remove(card)
        gm._pass_left_or_discard(player, card)
        return True
