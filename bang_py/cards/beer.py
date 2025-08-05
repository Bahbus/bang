"""Beer card from the base game. Heals 1 health if allowed by the game rules."""

from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


class BeerCard(BaseCard):
    card_name = "Beer"
    card_type = "action"
    card_set = "base"
    description = "Heals 1 health if allowed by the game rules."

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: "GameManager" | None = None,
    ) -> None:
        """Heal the target if allowed by game state and abilities."""
        if not target:
            return

        game = game or (player.metadata.game if player else None)
        game = game or target.metadata.game

        if game:
            if game.event_flags.get("no_beer_play"):
                return
            if game.event_flags.get("no_beer"):
                return
            alive = [p for p in game.players if p.is_alive()]
            if len(alive) <= 2:
                return
            heal_amt = int(game.event_flags.get("beer_heal", 1))
        else:
            heal_amt = 1

        if player and player.metadata.beer_heal_bonus:
            heal_amt += player.metadata.beer_heal_bonus

        if target.health < target.max_health:
            before = target.health
            target.heal(heal_amt)
            if game and target.health > before:
                game.on_player_healed(target)
