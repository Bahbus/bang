from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player

class DocHolyday(BaseCharacter):
    name = "Doc Holyday"
    description = (
        "Once during your turn, discard any two cards for a Bang! "
        "that doesn't count toward your limit."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(DocHolyday)
        return True

    def use_ability(
        self,
        gm: "GameManager",
        player: "Player",
        indices: list[int] | None = None,
    ) -> bool:
        if player.metadata.doc_used or len(player.hand) < 2:
            return True
        discard_indices = sorted(indices or list(range(2)), reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                gm._pass_left_or_discard(player, card)
        player.metadata.doc_used = True
        player.metadata.doc_free_bang += 1
        from ..cards.bang import BangCard

        player.hand.append(BangCard())
        return True
