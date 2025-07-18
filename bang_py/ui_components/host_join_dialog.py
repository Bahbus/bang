from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class HostJoinDialog(QtWidgets.QDialog):
    """Dialog for hosting or joining a game."""

    def __init__(self, mode: str = "host", parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Host Game" if mode == "host" else "Join Game")
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        if mode == "host":
            self.port_edit = QtWidgets.QLineEdit("8765")
            self.max_players_edit = QtWidgets.QLineEdit("7")
            layout.addRow("Host Port:", self.port_edit)
            layout.addRow("Max Players:", self.max_players_edit)
        else:
            self.addr_edit = QtWidgets.QLineEdit("localhost")
            self.port_edit = QtWidgets.QLineEdit("8765")
            self.code_edit = QtWidgets.QLineEdit()
            layout.addRow("Host Address:", self.addr_edit)
            layout.addRow("Port:", self.port_edit)
            layout.addRow("Room Code:", self.code_edit)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

