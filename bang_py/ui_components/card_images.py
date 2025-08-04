from __future__ import annotations

from importlib import resources
from typing import Dict

from PySide6 import QtCore, QtGui, QtWidgets
try:
    from PySide6 import QtMultimedia  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    QtMultimedia = None

try:
    from PySide6 import QtSvg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    QtSvg = None

from ..helpers import RankSuitIconLoader

DEFAULT_SIZE = (60, 90)
ASSETS_DIR = resources.files("bang_py") / "assets"
CHARACTER_DIR = ASSETS_DIR / "characters"
AUDIO_DIR = ASSETS_DIR / "audio"

_CARD_BACK_FILES = {
    "other": "other_card_back.png",
    "character": "character_card_back.png",
    "role": "role_card_back.png",
}

_TEMPLATE_FILES = {
    "blue": "template_blue.png",
    "brown": "template_brown.png",
    "green": "template_green.png",
    "character": "template_character.png",
    "role": "template_role.png",
    "high_noon": "template_highnoon_event.png",
    "fistful": "template_afistfulofcards_event.png",
}


def load_character_image(name: str, width: int = 60, height: int = 90) -> QtGui.QPixmap:
    """Return a portrait pixmap for ``name`` or a default image."""
    base = name.lower().replace(" ", "_")
    for ext in (".webp", ".png", ".jpg", ".jpeg"):
        path = CHARACTER_DIR / f"{base}{ext}"
        if path.exists():
            break
    else:
        path = CHARACTER_DIR / "default.webp"
    if not path.exists():
        pix = QtGui.QPixmap(width, height)
        pix.fill(QtGui.QColor("gray"))
        return pix
    with resources.as_file(path) as file_path:
        pix = QtGui.QPixmap(str(file_path))
    if pix.isNull():
        pix = QtGui.QPixmap(width, height)
        pix.fill(QtGui.QColor("gray"))
    else:
        pix = pix.scaled(
            width,
            height,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
    return pix


def load_sound(name: str) -> QtMultimedia.QSoundEffect | None:
    """Return a sound effect for ``name`` if QtMultimedia is available.

    Examples include ``"gunshot"``, ``"card_shuffle"`` and ``"ui_click"``.
    """
    if QtMultimedia is None:
        return None
    base = name.lower().replace(" ", "_")
    path = None
    for ext in (".wav", ".ogg"):
        candidate = AUDIO_DIR / f"{base}{ext}"
        if candidate.exists():
            path = candidate
            break
    if path is None:
        return None
    effect = QtMultimedia.QSoundEffect()
    with resources.as_file(path) as file_path:
        effect.setSource(QtCore.QUrl.fromLocalFile(str(file_path)))
    return effect


class CardImageLoader:
    """Load and compose card template and rank/suit images."""

    def __init__(self, width: int = 60, height: int = 90) -> None:
        self.width = width
        self.height = height
        self.templates = self._load_templates(width, height)
        self.card_backs = self._load_card_backs(width, height)
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
            with resources.as_file(path) as file_path:
                pix = QtGui.QPixmap(str(file_path))
            if pix.isNull():
                pix = cls._fallback_pixmap(width, height)
            else:
                pix = pix.scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            templates[key] = pix
        return templates

    @classmethod
    def _load_card_backs(
        cls, width: int, height: int
    ) -> Dict[str, QtGui.QPixmap]:
        backs: Dict[str, QtGui.QPixmap] = {}
        for key, fname in _CARD_BACK_FILES.items():
            path = ASSETS_DIR / fname
            with resources.as_file(path) as file_path:
                pix = QtGui.QPixmap(str(file_path))
            if pix.isNull():
                pix = cls._fallback_pixmap(width, height)
            else:
                pix = pix.scaled(
                    width,
                    height,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            backs[key] = pix
        return backs

    def get_template(self, name: str) -> QtGui.QPixmap:
        return self.templates.get(name, self._fallback_pixmap(self.width, self.height))

    def get_card_back(self, name: str) -> QtGui.QPixmap:
        """Return a card back pixmap for ``name``."""
        return self.card_backs.get(name, self._fallback_pixmap(self.width, self.height))

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
        """Return template name based on card ``type`` and ``set``."""

        match (card_type, card_set):
            case ("event", "fistful_of_cards"):
                return "fistful"
            case ("event", _):
                return "high_noon"
            case ("blue", _):
                return "blue"
            case ("green", _):
                return "green"
            case ("character", _):
                return "character"
            case ("role", _):
                return "role"
            case _:
                return "brown"


_card_image_loader: CardImageLoader | None = None


def get_loader() -> CardImageLoader:
    """Return a cached :class:`CardImageLoader` instance.

    The loader is created lazily after a ``QApplication`` exists to avoid
    issues with Qt objects being instantiated before the application.
    """

    if QtWidgets.QApplication.instance() is None:
        raise RuntimeError("QApplication must be instantiated before using CardImageLoader")

    global _card_image_loader
    if _card_image_loader is None:
        _card_image_loader = CardImageLoader(*DEFAULT_SIZE)
    return _card_image_loader

