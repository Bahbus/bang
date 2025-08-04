from __future__ import annotations

from PySide6 import QtCore, QtWidgets
try:
    from PySide6 import QtMultimedia  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    QtMultimedia = None

from .card_images import load_sound

"""Widgets for the initial menu.

Contains :class:`StartMenu` which asks for the player's name and offers
buttons to host or join a game or open settings.
"""


class StartMenu(QtWidgets.QWidget):
    """Main menu with options to host or join a game."""

    host_clicked = QtCore.Signal()
    join_clicked = QtCore.Signal()
    settings_clicked = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(200, 100, 200, 100)

        form = QtWidgets.QFormLayout()
        self.name_edit = QtWidgets.QLineEdit()
        form.addRow("Name:", self.name_edit)
        layout.addLayout(form)

        self.click_sound = load_sound("ui_click")

        host_btn = QtWidgets.QPushButton("Host Game")
        host_btn.clicked.connect(self._host)
        join_btn = QtWidgets.QPushButton("Join Game")
        join_btn.clicked.connect(self._join)
        settings_btn = QtWidgets.QPushButton("Settings")
        settings_btn.clicked.connect(self._settings)

        layout.addWidget(host_btn)
        layout.addWidget(join_btn)
        layout.addWidget(settings_btn)
        layout.addStretch(1)

    def _play_click(self) -> None:
        if self.click_sound:
            self.click_sound.play()

    def _host(self) -> None:
        self._play_click()
        self.host_clicked.emit()

    def _join(self) -> None:
        self._play_click()
        self.join_clicked.emit()

    def _settings(self) -> None:
        self._play_click()
        self.settings_clicked.emit()
