"""Utility helpers for card checks, ability resolution, and loading rank or suit icons."""

from __future__ import annotations

from .cards.card import BaseCard
from .player import Player
from .characters.base import BaseCharacter
from .characters.vera_custer import VeraCuster
from pathlib import Path
from typing import TYPE_CHECKING

try:  # Qt is optional for non-UI use
    from PySide6 import QtCore, QtGui, QtSvg
except ImportError:  # pragma: no cover - Qt may not be installed
    QtCore = QtGui = QtSvg = None  # type: ignore

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


class RankSuitIconLoader:
    """Return ``QPixmap`` fragments for ranks and suits from the SVG sheet."""

    _rank_order = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    _suit_order = ["Clubs", "Hearts", "Spades", "Diamonds"]

    def __init__(self, svg_path: str | None = None) -> None:
        if QtGui is None or QtSvg is None:
            raise ImportError("PySide6 is required for RankSuitIconLoader")
        if svg_path is None:
            svg_path = str(Path(__file__).with_name("assets") / "ranks_and_suits_sheet.svg")
        self.svg_path = svg_path
        self.cell_w = 64
        self.cell_h = 89
        self.sheet_w = self.cell_w * 13
        self.sheet_h = self.cell_h * 4
        self._sheet = self._load_sheet()
        self._cache: dict[tuple[str, str], QtGui.QPixmap] = {}

    def _load_sheet(self) -> QtGui.QPixmap:
        renderer = QtSvg.QSvgRenderer(self.svg_path)
        pixmap = QtGui.QPixmap(self.sheet_w, self.sheet_h)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def _norm_rank(self, rank: int | str) -> str:
        if isinstance(rank, int):
            if rank == 1:
                return "A"
            if 2 <= rank <= 10:
                return str(rank)
            if rank == 11:
                return "J"
            if rank == 12:
                return "Q"
            if rank == 13:
                return "K"
            raise ValueError(f"Invalid rank: {rank}")
        return rank.upper()

    def get_pixmap(self, rank: int | str, suit: str) -> QtGui.QPixmap:
        """Return an icon for ``rank`` and ``suit`` from the SVG sheet."""

        rank_str = self._norm_rank(rank)
        suit_name = suit.capitalize()
        key = (rank_str, suit_name)
        if key in self._cache:
            return self._cache[key]

        try:
            col = self._rank_order.index(rank_str)
        except ValueError as exc:  # pragma: no cover - checked via norm_rank
            raise ValueError(f"Unknown rank {rank}") from exc
        try:
            row = self._suit_order.index(suit_name)
        except ValueError as exc:
            raise ValueError(f"Unknown suit {suit}") from exc

        pix = self._sheet.copy(col * self.cell_w, row * self.cell_h, self.cell_w, self.cell_h)
        self._cache[key] = pix
        return pix
