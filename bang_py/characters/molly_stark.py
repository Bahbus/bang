"""Draw when playing or discarding out of turn, including Duels. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol
    from ..player import Player
    from ..cards.card import BaseCard


class MollyStark(BaseCharacter):
    name = "Molly Stark"
    description = (
        "Whenever you play or voluntarily discard any card out of turn, draw a card. "
        "If targeted by a Duel, draw for all Bangs played after the Duel ends."
    )
    starting_health = 4

    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        try:
            player.metadata = player.metadata or {}  # type: ignore[misc, assignment]
        except AttributeError:
            pass
        metadata: Any = player.metadata
        if isinstance(metadata, dict):
            metadata.setdefault("abilities", set()).add(MollyStark)
            metadata.setdefault("molly_choices", {})
        else:
            metadata.abilities.add(MollyStark)
            metadata.molly_choices = metadata.molly_choices or {}
        return True

    def on_out_of_turn_discard(
        self, gm: "GameManagerProtocol", player: "Player", card: "BaseCard"
    ) -> None:
        from ..cards.bang import BangCard

        counts = getattr(gm, "_duel_counts", None)
        if isinstance(card, BangCard) and counts is not None:
            name = player.name
            counts[name] = counts.get(name, 0) + 1
        else:
            gm.draw_card(player)
