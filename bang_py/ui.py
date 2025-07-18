import json
import secrets
from pathlib import Path
import os

from PySide6 import QtCore, QtGui, QtWidgets

if __package__ in {None, ""}:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "bang_py"

from .ui_components import (
    StartMenu,
    HostJoinDialog,
    GameView,
    ServerThread,
    ClientThread,
)


class BangUI(QtWidgets.QMainWindow):
    """Qt GUI for hosting, joining and playing a Bang game."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bang!")
        self.resize(1024, 768)
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #deb887;
                font-family: 'Courier New';
                font-size: 16px;
            }
            QPushButton {
                background-color: #f4a460;
                border: 2px solid #8b4513;
                min-width: 80px;
                max-width: 150px;
            }
            QLineEdit {
                background-color: #fff8dc;
                color: #000000;
            }
            """
        )

        self.client: ClientThread | None = None
        self.server_thread: ServerThread | None = None
        self.room_code = ""
        self.local_name = ""

        self._build_start_menu()
        self._create_log_dock()

    # Menu screens -----------------------------------------------------
    def _build_start_menu(self) -> None:
        self.start_menu = StartMenu()
        self.start_menu.host_clicked.connect(self._host_menu)
        self.start_menu.join_clicked.connect(self._join_menu)
        self.start_menu.settings_clicked.connect(self._settings_dialog)
        self.stack.addWidget(self.start_menu)
        self.stack.setCurrentWidget(self.start_menu)

    def _host_menu(self) -> None:
        dialog = HostJoinDialog("host", self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                port = int(dialog.port_edit.text())
                max_players = int(dialog.max_players_edit.text())
            except ValueError:
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid settings")
                return
            self._start_host(port, max_players)

    def _join_menu(self) -> None:
        dialog = HostJoinDialog("join", self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            addr = dialog.addr_edit.text().strip()
            code = dialog.code_edit.text().strip()
            try:
                port = int(dialog.port_edit.text())
            except ValueError:
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid port")
                return
            self._start_join(addr, port, code)

    def _settings_dialog(self) -> None:
        QtWidgets.QMessageBox.information(self, "Settings",
                                          "Settings dialog placeholder")

    # Game view --------------------------------------------------------
    def _build_game_view(self) -> None:
        self.game_view = GameView()
        self.game_view.action_signal.connect(self._send_action)
        self.game_view.end_turn_signal.connect(self._end_turn)
        self.board = self.game_view.board
        self.player_list = self.game_view.player_list
        self.hand_layout = self.game_view.hand_layout
        self.stack.addWidget(self.game_view)
        self.stack.setCurrentWidget(self.game_view)

    def _create_log_dock(self) -> None:
        self.log_dock = QtWidgets.QDockWidget("Log", self)
        self.log_dock.setFloating(True)
        self.log_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.log_dock.setWindowFlags(
            self.log_dock.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
        )
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white;"
        )
        self.log_dock.setWidget(self.log_text)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.log_dock)
        self.log_dock.show()

    # Networking -------------------------------------------------------
    def _start_host(self, port: int, max_players: int) -> None:
        name = self.start_menu.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Please enter your name")
            return
        room_code = secrets.token_hex(3)
        self.server_thread = ServerThread("", port, room_code, [], max_players)
        self.server_thread.start()
        uri = f"ws://localhost:{port}"
        self._start_client(uri, room_code)
        self.setWindowTitle(f"Bang! - {room_code}")

    def _start_join(self, addr: str, port: int, code: str) -> None:
        name = self.start_menu.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Please enter your name")
            return
        uri = f"ws://{addr}:{port}"
        self._start_client(uri, code)

    def _start_client(self, uri: str, code: str) -> None:
        self.room_code = code
        self.client = ClientThread(uri, code, self.start_menu.name_edit.text().strip())
        self.client.message_received.connect(self._append_message)
        self.client.start()
        self.local_name = self.start_menu.name_edit.text().strip()
        self._build_game_view()
        self.log_dock.show()

    def _append_message(self, msg: str) -> None:
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            self.log_text.append(msg)
            return

        if isinstance(data, dict):
            if "message" in data:
                self.log_text.append(data["message"])
            if "players" in data:
                self._update_players(data["players"])
            if "hand" in data:
                self._update_hand(data["hand"])
            if "prompt" in data:
                self._show_prompt(data["prompt"], data)
        else:
            self.log_text.append(str(data))

    def _end_turn(self) -> None:
        if self.client:
            self.client.send_end_turn()

    def _send_action(self, payload: dict) -> None:
        if self.client:
            self.client.send_json(payload)

    def _update_players(self, players: list[dict]) -> None:
        if hasattr(self, "game_view"):
            self.game_view.update_players(players, self.local_name)

    def _update_hand(self, cards: list[str]) -> None:
        if hasattr(self, "game_view"):
            self.game_view.update_hand(cards)

    def _show_prompt(self, prompt: str, data: dict) -> None:
        if prompt == "general_store":
            cards = data.get("cards", [])
            item, ok = QtWidgets.QInputDialog.getItem(
                self, "General Store", "Pick a card:", cards, 0, False
            )
            if ok:
                index = cards.index(item)
                self._send_action({"action": "general_store_pick", "index": index})
        elif "options" in data:
            opts = [o.get("name", str(i)) for i, o in enumerate(data["options"])]
            item, ok = QtWidgets.QInputDialog.getItem(
                self, prompt.replace("_", " ").title(), "Choose:", opts, 0, False
            )
            if ok:
                idx = opts.index(item)
                self._send_action(
                    {
                        "action": "use_ability",
                        "ability": prompt,
                        "target": data["options"][idx]["index"],
                    }
                )
        else:
            self.log_text.append(f"Prompt: {prompt}")

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Toggle full-screen mode when F11 is pressed."""
        if event.key() == QtCore.Qt.Key_F11:
            fs = QtCore.Qt.WindowFullScreen
            if self.windowState() & fs:
                self.setWindowState(self.windowState() & ~fs)
            else:
                self.setWindowState(self.windowState() | fs)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: D401
        """Handle window close and stop threads."""
        if self.client:
            self.client.stop()
            self.client.wait(1000)
            self.client = None
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait(1000)
            self.server_thread = None
        QtWidgets.QApplication.quit()
        super().closeEvent(event)


def main() -> None:
    """Start the Qt interface."""
    app = QtWidgets.QApplication([])
    ui = BangUI()
    ui.showMaximized()
    if os.getenv("BANG_AUTO_CLOSE"):
        QtCore.QTimer.singleShot(100, ui.close)
    app.exec()


if __name__ == "__main__":
    main()
