from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager import GameManager


class TequilaCard(Card):
    """Heal one health by discarding another card."""

    card_name = "Tequila"
    description = "Discard another card with Tequila to heal 1 health."

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
        before = target.health
        target.heal(1)
        if target.health > before:
            game.on_player_healed(target)

