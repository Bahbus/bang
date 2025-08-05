from __future__ import annotations

from importlib import resources

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
ICON_DIR = ASSETS_DIR / "icons"

# Mapping of card/ability identifiers to icon filenames.
ACTION_ICON_MAP = {
    "bang": "bang_icon.webp",
    "missed": "missed_icon.webp",
    "any_player": "any_player_icon.webp",
    "all_players": "all_players_icon.webp",
    "any_reachable_player": "any_reachable_player_icon.webp",
    "draw_card": "draw_card_icon.webp",
    "discard_card": "discard_card_icon.webp",
    "discard_another_card": "discard_another_card_icon.webp",
    "gain_life": "gain_life_icon.webp",
    "range_1": "range_1_icon.webp",
    "range_2": "range_2_icon.webp",
    "range_3": "range_3_icon.webp",
    "range_4": "range_4_icon.webp",
    "range_5": "range_5_icon.webp",
}

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


def load_sound(name: str, parent: QtCore.QObject | None = None) -> QtCore.QObject | None:
    """Return a playable sound object for ``name``.

    The loader searches for ``.mp3``, ``.wav`` and ``.ogg`` files in that order.
    If a ``.mp3`` file is found a :class:`QMediaPlayer` with an accompanying
    :class:`QAudioOutput` is returned, otherwise a :class:`QSoundEffect` is used.
    The returned object is parented to ``parent`` so resources are released when
    the parent is deleted.
    """

    if QtMultimedia is None:
        return None

    class _MediaPlayer(QtMultimedia.QMediaPlayer):
        """Small helper to ensure playback stops when deleted."""

        def __del__(self) -> None:  # pragma: no cover - best effort
            try:
                self.stop()
            except Exception:
                pass
    base = name.lower().replace(" ", "_")
    path = None
    for ext in (".mp3", ".wav", ".ogg"):
        candidate = AUDIO_DIR / f"{base}{ext}"
        if candidate.exists():
            path = candidate
            break
    if path is None:
        return None
    with resources.as_file(path) as file_path:
        url = QtCore.QUrl.fromLocalFile(str(file_path))
    if path.suffix == ".mp3":
        player = _MediaPlayer(parent)
        audio_out = QtMultimedia.QAudioOutput(player)
        player.setAudioOutput(audio_out)
        player.setSource(url)
        return player
    effect = QtMultimedia.QSoundEffect(parent)
    effect.setSource(url)
    return effect


class CardImageLoader:
    """Load and compose card template and rank/suit images."""

    def __init__(self, width: int = 60, height: int = 90) -> None:
        self.width = width
        self.height = height
        self.templates = self._load_templates(width, height)
        self.card_backs = self._load_card_backs(width, height)
        self.rank_loader = RankSuitIconLoader()
        self.action_icons = self._load_action_icons()

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
    ) -> dict[str, QtGui.QPixmap]:
        templates: dict[str, QtGui.QPixmap] = {}
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
    ) -> dict[str, QtGui.QPixmap]:
        backs: dict[str, QtGui.QPixmap] = {}
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

    @classmethod
    def _load_action_icons(cls) -> dict[str, QtGui.QPixmap]:
        icons: dict[str, QtGui.QPixmap] = {}
        for key, fname in ACTION_ICON_MAP.items():
            path = ICON_DIR / fname
            with resources.as_file(path) as file_path:
                pix = QtGui.QPixmap(str(file_path))
            if pix.isNull():
                pix = cls._fallback_pixmap(int(DEFAULT_SIZE[0] * 0.4), int(DEFAULT_SIZE[1] * 0.4))
            icons[key] = pix
        return icons

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
        name: str | None = None,
    ) -> QtGui.QPixmap:
        """Return a card pixmap with optional rank/suit and action icon overlays."""
        template_name = self._template_for(card_type, card_set)
        base = self.get_template(template_name).copy()
        painter = QtGui.QPainter(base)
        if rank is not None and suit is not None:
            icon = self.rank_loader.get_pixmap(rank, suit)
            icon = icon.scaled(
                int(self.width * 0.6),
                int(self.height * 0.6),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            x = (self.width - icon.width()) // 2
            y = (self.height - icon.height()) // 2
            painter.drawPixmap(x, y, icon)
        if name:
            key = name.lower().replace("!", "").replace(" ", "_")
            action_icon = self.action_icons.get(key)
            if action_icon and not action_icon.isNull():
                action_icon = action_icon.scaled(
                    int(self.width * 0.35),
                    int(self.width * 0.35),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
                x = self.width - action_icon.width()
                y = self.height - action_icon.height()
                painter.drawPixmap(x, y, action_icon)
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

