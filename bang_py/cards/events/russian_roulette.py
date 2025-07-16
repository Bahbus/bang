from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from ..roles import SheriffRoleCard
from ..missed import MissedCard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class RussianRouletteEventCard(BaseEventCard):
    """When Russian Roulette enters play, starting with the Sheriff each player
    discards a Missed! The first not to do so loses 2 life points."""

    card_name = "Russian Roulette"
    card_set = "fistful_of_cards"
    description = (
        "When Russian Roulette enters play, starting with the Sheriff each player "
        "discards a Missed! The first not to do so loses 2 life points."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        players = [p for p in game.players if p.is_alive()]
        start = next(
            (i for i, p in enumerate(players) if isinstance(p.role, SheriffRoleCard)),
            0,
        )
        for offset in range(len(players)):
            p = players[(start + offset) % len(players)]
            miss = next((c for c in p.hand if isinstance(c, MissedCard)), None)
            if miss:
                p.hand.remove(miss)
                game.discard_pile.append(miss)
            else:
                p.take_damage(2)
                game.on_player_damaged(p)
                break
