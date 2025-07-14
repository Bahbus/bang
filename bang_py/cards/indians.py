from __future__ import annotations

from .card import BaseCard
from ..player import Player
from ..helpers import handle_out_of_turn_discard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class IndiansCard(BaseCard):
    card_name = "Indians!"
    card_type = "action"
    card_set = "base"
    description = "Others discard Bang! or suffer 1 damage."

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not game or not player:
            return
        from .bang import BangCard

        for p in game.players:
            if p is player:
                continue
            bang = next((c for c in p.hand if isinstance(c, BangCard)), None)
            if bang:
                p.hand.remove(bang)
                game.discard_pile.append(bang)
                handle_out_of_turn_discard(game, p, bang)
            else:
                before = p.health
                p.take_damage(1)
                if p.health < before:
                    game.on_player_damaged(p, player)
