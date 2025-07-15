from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player
    from ..cards.card import BaseCard

class JohnnyKisch(BaseCharacter):
    name = "Johnny Kisch"
    description = (
        "Each time you put a card into play, discard all other cards with the same name in play."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(JohnnyKisch)

        def on_play(p: "Player", card: "BaseCard", _t: "Player | None") -> None:
            if p is player and hasattr(card, "card_name"):
                for o in gm.players:
                    if card.card_name in o.equipment:
                        existing = o.unequip(card.card_name)
                        if existing and existing is not card:
                            gm._pass_left_or_discard(o, existing)

        gm.card_played_listeners.append(on_play)
        return True
