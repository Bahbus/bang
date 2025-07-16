from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager

from ..helpers import handle_out_of_turn_discard


class RagTimeCard(BaseCard):
    """Discard a card to steal one from any player."""

    card_name = "Rag Time"
    card_type = "action"
    card_set = "fistful_of_cards"
    description = "Discard another card to take a card from any player."

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        *,
        discard_idx: int = 0,
        steal_idx: int = 0,
    ) -> None:
        if not target or not player or not game or not player.hand:
            return
        if 0 <= discard_idx < len(player.hand):
            discard = player.hand.pop(discard_idx)
        else:
            discard = player.hand.pop(0)
        game.discard_pile.append(discard)
        handle_out_of_turn_discard(game, player, discard)

        if target.hand:
            idx = steal_idx if 0 <= steal_idx < len(target.hand) else 0
            card = target.hand.pop(idx)
            player.hand.append(card)
        elif target.equipment:
            card = next(iter(target.equipment.values()))
            target.unequip(card.card_name)
            player.hand.append(card)
