"""General Store card helper methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .cards.card import BaseCard
from .game_manager_protocol import GameManagerProtocol

if TYPE_CHECKING:
    from .player import Player


class GeneralStoreMixin:
    """Mixin implementing General Store management."""

    general_store_cards: list[BaseCard] | None
    general_store_order: list["Player"] | None
    general_store_index: int
    deck: object
    discard_pile: list[BaseCard]
    _players: list["Player"]

    def start_general_store(self: GameManagerProtocol, player: "Player") -> list[str]:
        if not self.deck:
            self.general_store_cards = []
            self.general_store_order = []
            self.general_store_index = 0
            return []
        self.general_store_cards = self._deal_general_store_cards()
        self._set_general_store_order(player)
        return [c.card_name for c in self.general_store_cards or []]

    def _deal_general_store_cards(self: GameManagerProtocol) -> list[BaseCard]:
        alive = [p for p in self._players if p.is_alive()]
        cards: list[BaseCard] = []
        for _ in range(len(alive)):
            card = self._draw_from_deck()
            if card:
                cards.append(card)
        return cards

    def _set_general_store_order(self: GameManagerProtocol, player: "Player") -> None:
        start_idx = self._players.index(player)
        order: list["Player"] = []
        for i in range(len(self._players)):
            p = self._players[(start_idx + i) % len(self._players)]
            if p.is_alive():
                order.append(p)
        self.general_store_order = order
        self.general_store_index = 0

    def general_store_pick(self: GameManagerProtocol, player: "Player", index: int) -> bool:
        if not self._valid_general_store_pick(player, index):
            return False
        if self.general_store_cards is None or self.general_store_order is None:
            return False
        card = self.general_store_cards.pop(index)
        player.hand.append(card)
        self.general_store_index += 1
        if self.general_store_index >= len(self.general_store_order):
            self._cleanup_general_store_leftovers()
        return True

    def _valid_general_store_pick(self: GameManagerProtocol, player: "Player", index: int) -> bool:
        cards = self.general_store_cards
        order = self.general_store_order
        if (
            not cards
            or not order
            or self.general_store_index >= len(order)
            or order[self.general_store_index] is not player
        ):
            return False
        return 0 <= index < len(cards)

    def _cleanup_general_store_leftovers(self: GameManagerProtocol) -> None:
        for leftover in self.general_store_cards:
            self.discard_pile.append(leftover)
        self.general_store_cards = None
        self.general_store_order = None
        self.general_store_index = 0
