"""Duel card from the base game. Players alternate discarding Bang! cards; loser takes 1 damage."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from ..helpers import handle_out_of_turn_discard
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class DuelCard(BaseCard):
    card_name = "Duel"
    card_type = "action"
    card_set = "base"
    description = "Players alternate discarding Bang! cards; loser takes 1 damage."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        if not target or not player or not game:
            return
        from .bang import BangCard

        attacker = target
        defender = player
        game._duel_counts = {}
        while True:
            bang = next((c for c in attacker.hand if isinstance(c, BangCard)), None)
            if bang:
                attacker.hand.remove(bang)
                game.discard_pile.append(bang)
                handle_out_of_turn_discard(game, attacker, bang)
                attacker, defender = defender, attacker
            else:
                before = attacker.health
                attacker.take_damage(1)
                if attacker.health < before:
                    game.on_player_damaged(attacker, defender)
                break
        for pname, count in getattr(game, "_duel_counts", {}).items():
            pl = next((pl for pl in game.players if pl.name == pname), None)
            if pl:
                for _ in range(count):
                    game.draw_card(pl)
        game._duel_counts = None
