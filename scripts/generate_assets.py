from __future__ import annotations

import struct
import math
import wave
from pathlib import Path

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtWidgets

ASSETS_DIR = Path(__file__).resolve().parents[1] / "bang_py" / "assets"
CHAR_DIR = ASSETS_DIR / "characters"
AUDIO_DIR = ASSETS_DIR / "audio"


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


def create_beep(path: Path) -> None:
    if path.exists():
        return
    rate = 44100
    duration = 0.1
    freq = 440
    volume = 0.5
    frames = [
        struct.pack('<h', int(volume * math.sin(2 * math.pi * freq * i / rate) * 32767))
        for i in range(int(duration * rate))
    ]
    with wave.open(str(path), 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(b''.join(frames))


def main() -> None:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    create_default_image(CHAR_DIR / "default.png")
    create_beep(AUDIO_DIR / "beep.wav")


if __name__ == "__main__":
    main()
