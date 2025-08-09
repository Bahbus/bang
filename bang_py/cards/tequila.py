"""Tequila card from the Fistful of Cards expansion. Discard another card with Tequila to heal 1
health."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class TequilaCard(BaseCard):
    """Heal one health by discarding another card."""

    card_name = "Tequila"
    card_type = "action"
    card_set = "fistful_of_cards"
    description = "Discard another card with Tequila to heal 1 health."

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
        before = target.health
        target.heal(1)
        if target.health > before:
            game.on_player_healed(target)
