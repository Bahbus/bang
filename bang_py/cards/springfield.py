from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager

from .bang import BangCard
from ..helpers import handle_out_of_turn_discard


class SpringfieldCard(BaseCard):
    """Discard a card to Bang! any player."""

    card_name = "Springfield"
    card_type = "action"
    card_set = "dodge_city"
    description = "Discard another card to Bang! any player."

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        *,
        discard_idx: int = 0,
    ) -> None:
        if not target or not player or not game or not player.hand:
            return
        if 0 <= discard_idx < len(player.hand):
            discard = player.hand.pop(discard_idx)
        else:
            discard = player.hand.pop(0)
        game.discard_pile.append(discard)
        handle_out_of_turn_discard(game, player, discard)
        if not game._auto_miss(target):
            BangCard().play(
                target,
                game.deck,
                ignore_equipment=player.metadata.ignore_others_equipment,
            )
            if target.health < target.max_health:
                game.on_player_damaged(target, player)


