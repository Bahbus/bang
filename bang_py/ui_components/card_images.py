from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from PySide6 import QtCore, QtGui

try:
    from PySide6 import QtSvg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    QtSvg = None

from ..helpers import RankSuitIconLoader

DEFAULT_SIZE = (60, 90)
ASSETS_DIR = Path(__file__).resolve().with_name("assets")

_TEMPLATE_FILES = {
    "blue": "template_blue.png",
    "brown": "template_brown.png",
    "green": "template_green.png",
    "character": "template_character.png",
    "role": "template_role.png",
    "high_noon": "template_highnoon_event.png",
    "fistful": "template_afistfulofcards_event.png",
}


class CardImageLoader:
    """Load and compose card template and rank/suit images."""

    def __init__(self, width: int = 60, height: int = 90) -> None:
        self.width = width
        self.height = height
        self.templates = self._load_templates(width, height)
        self.rank_loader = RankSuitIconLoader()

    @staticmethod
    def _fallback_pixmap(width: int, height: int) -> QtGui.QPixmap:
        pix = QtGui.QPixmap(width, height)
        pix.fill(QtGui.QColor("#f4e1b5"))
        painter = QtGui.QPainter(pix)
        pen = QtGui.QPen(QtGui.QColor("#8b4513"))
        painter.setPen(pen)
        painter.drawRect(0, 0, width - 1, height - 1)
        painter.end()
        return pix

    @classmethod
    def _load_templates(
        cls, width: int, height: int
    ) -> Dict[str, QtGui.QPixmap]:
        templates: Dict[str, QtGui.QPixmap] = {}
        for key, fname in _TEMPLATE_FILES.items():
            path = ASSETS_DIR / fname
            pix = QtGui.QPixmap(str(path))
            if pix.isNull():
                pix = cls._fallback_pixmap(width, height)
            else:
                pix = pix.scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            templates[key] = pix
        return templates

    def get_template(self, name: str) -> QtGui.QPixmap:
        return self.templates.get(name, self._fallback_pixmap(self.width, self.height))

    def compose_card(
        self,
        card_type: str,
        rank: int | str | None = None,
        suit: str | None = None,
        card_set: str | None = None,
    ) -> QtGui.QPixmap:
        """Return a card pixmap for ``card_type`` with optional rank and suit."""
        template_name = self._template_for(card_type, card_set)
        base = self.get_template(template_name).copy()
        if rank is not None and suit is not None:
            icon = self.rank_loader.get_pixmap(rank, suit)
            icon = icon.scaled(int(self.width * 0.6), int(self.height * 0.6), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            painter = QtGui.QPainter(base)
            x = (self.width - icon.width()) // 2
            y = (self.height - icon.height()) // 2
            painter.drawPixmap(x, y, icon)
            painter.end()
        return base

    @staticmethod
    def _template_for(card_type: str, card_set: str | None) -> str:
        if card_type == "blue":
            return "blue"
        if card_type == "green":
            return "green"
        if card_type == "character":
            return "character"
        if card_type == "role":
            return "role"
        if card_type == "event":
            if card_set == "fistful_of_cards":
                return "fistful"
            return "high_noon"
        return "brown"


card_image_loader = CardImageLoader(*DEFAULT_SIZE)

