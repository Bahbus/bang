"""Utility helpers for card checks and ability resolution."""

from __future__ import annotations

from .cards.card import BaseCard
from .player import Player
from .characters.base import BaseCharacter
from .characters.vera_custer import VeraCuster
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .game_manager import GameManager


def is_heart(card: BaseCard | None) -> bool:
    """Return True if the drawn card is a Heart."""
    return getattr(card, "suit", None) == "Hearts"


def is_spade_between(card: BaseCard | None, low: int, high: int) -> bool:
    """Return True if card is a Spade with rank in [low, high]."""
    if getattr(card, "suit", None) != "Spades":
        return False
    rank = getattr(card, "rank", None)
    return rank is not None and low <= rank <= high


def has_ability(player: Player, char_cls: type[BaseCharacter]) -> bool:
    """Return True if the player effectively has the given character ability."""
    game = getattr(player.metadata, "game", None)
    if game and game.event_flags.get("no_abilities"):
        return False
    if isinstance(player.character, char_cls):
        return True
    if isinstance(player.character, VeraCuster):
        copied = player.metadata.vera_copy
        if copied and issubclass(copied, char_cls):
            return True
    return char_cls in getattr(player.metadata, "abilities", set())


def handle_out_of_turn_discard(game: "GameManager", player: Player, card: BaseCard) -> None:
    """Notify the player's character of an out-of-turn discard."""
    if not game or not player:
        return
    active = None
    if game.turn_order and 0 <= game.current_turn < len(game.turn_order):
        active = game.players[game.turn_order[game.current_turn]]
    if player is active:
        return
    if player.character and hasattr(player.character, "on_out_of_turn_discard"):
        player.character.on_out_of_turn_discard(game, player, card)
