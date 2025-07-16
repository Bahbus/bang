from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player
    from ..cards.card import BaseCard
    from ..cards.duel import DuelCard


class ApacheKid(BaseCharacter):
    name = "Apache Kid"
    description = "You are unaffected by Diamond suited cards."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(ApacheKid)


        def check(p: "Player", card: "BaseCard", target: "Player | None") -> bool:
            if (
                p is not player
                and target is player
                and getattr(card, "suit", None) == "Diamonds"
            ):
                if gm._duel_counts is not None and not isinstance(card, DuelCard):
                    return True
                if card in getattr(p, "hand", []):
                    p.hand.remove(card)
                gm._pass_left_or_discard(p, card)
                return False
            return True

        gm.card_play_checks.append(check)
        return True
