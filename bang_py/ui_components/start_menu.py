from __future__ import annotations

from PySide6 import QtCore, QtWidgets


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

        host_btn = QtWidgets.QPushButton("Host Game")
        host_btn.clicked.connect(self.host_clicked)
        join_btn = QtWidgets.QPushButton("Join Game")
        join_btn.clicked.connect(self.join_clicked)
        settings_btn = QtWidgets.QPushButton("Settings")
        settings_btn.clicked.connect(self.settings_clicked)

        layout.addWidget(host_btn)
        layout.addWidget(join_btn)
        layout.addWidget(settings_btn)
        layout.addStretch(1)

