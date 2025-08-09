"""Draw when playing or discarding out of turn, including Duels. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player
    from ..cards.card import BaseCard


class MollyStark(BaseCharacter):
    name = "Molly Stark"
    description = (
        "Whenever you play or voluntarily discard any card out of turn, draw a card. "
        "If targeted by a Duel, draw for all Bangs played after the Duel ends."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(MollyStark)
        if player.metadata.molly_choices is None:
            player.metadata.molly_choices = {}
        return True

    def on_out_of_turn_discard(self, gm: "GameManager", player: "Player", card: "BaseCard") -> None:
        from ..cards.bang import BangCard

        if isinstance(card, BangCard) and getattr(gm, "_duel_counts", None) is not None:
            name = player.name
            gm._duel_counts[name] = gm._duel_counts.get(name, 0) + 1
        else:
            gm.draw_card(player)
