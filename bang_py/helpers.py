from __future__ import annotations

from .cards.card import Card
from .player import Player
from .characters import Character, VeraCuster
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .game_manager import GameManager


def is_heart(card: Card | None) -> bool:
    """Return True if the drawn card is a Heart."""
    return getattr(card, "suit", None) == "Hearts"


def is_spade_between(card: Card | None, low: int, high: int) -> bool:
    """Return True if card is a Spade with rank in [low, high]."""
    if getattr(card, "suit", None) != "Spades":
        return False
    rank = getattr(card, "rank", None)
    return rank is not None and low <= rank <= high


def has_ability(player: Player, char_cls: Type[Character]) -> bool:
    """Return True if the player effectively has the given character ability."""
    if isinstance(player.character, char_cls):
        return True
    if isinstance(player.character, VeraCuster):
        copied = player.metadata.vera_copy
        return bool(copied and issubclass(copied, char_cls))
    return False


def handle_out_of_turn_discard(game: "GameManager", player: Player, card: Card) -> None:
    """Trigger Molly Stark ability when appropriate for a discarded card."""
    if not game or not player:
        return
    active = None
    if game.turn_order and 0 <= game.current_turn < len(game.turn_order):
        active = game.players[game.turn_order[game.current_turn]]
    if player is active:
        return
    from .characters import MollyStark
    from .cards.bang import BangCard
    from .cards.missed import MissedCard
    from .cards.beer import BeerCard

    if has_ability(player, MollyStark) and isinstance(card, (BangCard, MissedCard, BeerCard)):
        game.draw_card(player)
