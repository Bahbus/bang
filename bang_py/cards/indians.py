from __future__ import annotations

from .card import Card
from ..player import Player
from ..characters import MollyStark
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager
    from .bang import BangCard


class IndiansCard(Card):
    card_name = "Indians!"

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
                if isinstance(p.character, MollyStark):
                    game.draw_card(p)
            else:
                before = p.health
                p.take_damage(1)
                if p.health < before:
                    game.on_player_damaged(p, player)
