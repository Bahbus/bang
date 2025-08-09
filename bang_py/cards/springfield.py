"""Springfield card from the Dodge City expansion. Discard another card to Bang! any player."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol

from .bang import BangCard
from ..helpers import handle_out_of_turn_discard


class SpringfieldCard(BaseCard):
    """Discard a card to Bang! any player."""

    card_name = "Springfield"
    card_type = "action"
    card_set = "dodge_city"
    description = "Discard another card to Bang! any player."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        *,
        discard_idx: int = 0,
        **kwargs: Any,
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
                game=game,
                ignore_equipment=player.metadata.ignore_others_equipment,
            )
            if target.health < target.max_health:
                game.on_player_damaged(target, player)
