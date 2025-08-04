"""Generate placeholder portraits and simple sound effects.

This script creates coloured images for each character defined in the game and
short sine wave tones used as placeholder MP3 sound effects. It is executed in
the test suite and can also be run manually before packaging the game. If MP3
encoding is unavailable the sound files are simply skipped.
"""

from __future__ import annotations

import struct
import math
from pathlib import Path

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtWidgets
from importlib import import_module

ASSETS_DIR = Path(__file__).resolve().parents[1] / "bang_py" / "assets"
CHAR_DIR = ASSETS_DIR / "characters"
AUDIO_DIR = ASSETS_DIR / "audio"


def slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


def character_names() -> list[str]:
    mod = import_module("bang_py.characters")
    names: list[str] = []
    for attr in getattr(mod, "__all__", []):
        if attr == "BaseCharacter":
            continue
        cls = getattr(mod, attr)
        names.append(getattr(cls, "name", attr))
    return names


def create_default_image(path: Path) -> None:
    if path.exists():
        return
    app_created = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app_created = True
        app = QtWidgets.QApplication([])
    image = QtGui.QImage(60, 90, QtGui.QImage.Format_ARGB32)
    image.fill(QtGui.QColor("gray"))
    painter = QtGui.QPainter(image)
    painter.setPen(QtGui.QColor("darkgray"))
    painter.drawRect(0, 0, 59, 89)
    painter.setPen(QtGui.QColor("black"))
    font = QtGui.QFont()
    font.setPointSize(16)
    painter.setFont(font)
    painter.drawText(QtCore.QRect(0, 0, 60, 90), QtCore.Qt.AlignCenter, "?")
    painter.end()
    image.save(str(path))
    if app_created:
        app.quit()


def create_character_image(name: str, path: Path) -> None:
    if path.exists():
        return
    app_created = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app_created = True
        app = QtWidgets.QApplication([])
    image = QtGui.QImage(60, 90, QtGui.QImage.Format_ARGB32)
    hue = hash(name) % 360
    color = QtGui.QColor.fromHsl(hue, 128, 200)
    image.fill(color)
    painter = QtGui.QPainter(image)
    painter.setPen(QtGui.QColor("black"))
    font = QtGui.QFont()
    font.setPointSize(12)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(QtCore.QRect(0, 0, 60, 90), QtCore.Qt.AlignCenter, name[0])
    painter.end()
    image.save(str(path))
    if app_created:
        app.quit()


def create_beep(path: Path, freq: int = 440) -> None:
    """Create a short sine wave tone at ``path``.

    The function attempts to write an MP3 file. If the :mod:`pydub` package or
    an MP3 encoder is unavailable the file is not created.
    """

    if path.exists():
        return
    rate = 44100
    duration = 0.1
    volume = 0.5
    frames = [
        struct.pack('<h', int(volume * math.sin(2 * math.pi * freq * i / rate) * 32767))
        for i in range(int(duration * rate))
    ]
    raw = b"".join(frames)
    try:  # Attempt MP3 export
        from pydub import AudioSegment  # type: ignore
    except Exception:
        return
    audio = AudioSegment(
        data=raw,
        sample_width=2,
        frame_rate=rate,
        channels=1,
    )
    audio.export(str(path), format="mp3")


def main() -> None:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    # Skip regeneration if portraits exist and at least one real audio file is present
    char_paths = [CHAR_DIR / f"{slugify(n)}.webp" for n in character_names()]
    char_paths.append(CHAR_DIR / "default.webp")
    existing_audio = list(AUDIO_DIR.glob("*.mp3")) + list(AUDIO_DIR.glob("*.ogg"))
    if all(p.exists() for p in char_paths) and existing_audio:
        print("Assets already present, skipping generation")
        return
    create_default_image(CHAR_DIR / "default.webp")
    for name in character_names():
        create_character_image(name, CHAR_DIR / f"{slugify(name)}.webp")
    if not existing_audio:
        sounds = {
            "bang": 440,
            "draw_card": 660,
            "shuffle_cards": 550,
            "ui_click": 880,
        }
        for name, freq in sounds.items():
            create_beep(AUDIO_DIR / f"{name}.mp3", freq)


if __name__ == "__main__":
    main()
