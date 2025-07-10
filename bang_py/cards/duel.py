from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager
    from .bang import BangCard


class DuelCard(Card):
    card_name = "Duel"

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not target or not player or not game:
            return
        from .bang import BangCard

        attacker = target
        defender = player
        while True:
            bang = next((c for c in attacker.hand if isinstance(c, BangCard)), None)
            if bang:
                attacker.hand.remove(bang)
                game.discard_pile.append(bang)
                attacker, defender = defender, attacker
            else:
                before = attacker.health
                attacker.take_damage(1)
                if attacker.health < before:
                    game.on_player_damaged(attacker, defender)
                break
