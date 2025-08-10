"""Dead Man card from Fistful of Cards. First eliminated player returns with 2 life and 2 cards."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class DeadManEventCard(BaseEventCard):
    """Return the first eliminated player with two life and two cards."""

    card_name = "Dead Man"
    card_set = "fistful_of_cards"
    description = (
        "During his turn, the player that was eliminated first comes back with 2 life "
        "and 2 cards."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Dead Man event."""
        if game:
            game.event_flags["dead_man"] = True
            player_obj = game.first_eliminated
            if player_obj and not player_obj.is_alive():
                idx = game.players.index(player_obj)
                if idx not in game.turn_order:
                    insert_pos = (game.current_turn + 1) % (len(game.turn_order) + 1)
                    game.turn_order.insert(insert_pos, idx)
                    if insert_pos <= game.current_turn:
                        game.current_turn += 1
                game.event_flags["dead_man_player"] = player_obj
