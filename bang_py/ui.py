import json
import secrets
from pathlib import Path
import os

from PySide6 import QtCore, QtGui, QtWidgets, QtQuickWidgets

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "bang_py"

from .ui_components import (
    HostJoinDialog,
    GameView,
    ServerThread,
    ClientThread,
)
from .theme import get_stylesheet, get_current_theme
from .network.server import parse_join_token
from cryptography.fernet import InvalidToken


class BangUI(QtWidgets.QMainWindow):
    """Qt GUI for hosting, joining and playing a Bang game."""

    def __init__(self, theme: str | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Bang!")
        self.resize(1024, 768)
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        self.theme = theme or get_current_theme()
        self.setStyleSheet(get_stylesheet(self.theme))

        self.client: ClientThread | None = None
        self.server_thread: ServerThread | None = None
        self.room_code = ""
        self.local_name = ""
        self.menu_root: QtCore.QObject | None = None

        self._build_start_menu()

    def _get_player_name(self) -> str:
        if self.menu_root is not None:
            name = self.menu_root.property("nameText")
            if isinstance(name, str):
                name = name.strip()
                if name and len(name) <= 20 and name.isprintable():
                    return name
        return ""

    def _transition_to(self, widget: QtWidgets.QWidget) -> None:
        """Fade in the given widget on the stacked layout."""
        if self.stack.indexOf(widget) == -1:
            self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        effect = QtWidgets.QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0)
        anim = QtCore.QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
        self._current_anim = anim

    # Menu screens -----------------------------------------------------
    def _build_start_menu(self) -> None:
        qml_dir = Path(__file__).resolve().parent / "qml"
        self.start_menu = QtQuickWidgets.QQuickWidget()
        self.start_menu.setResizeMode(QtQuickWidgets.QQuickWidget.SizeRootObjectToView)
        self.start_menu.setSource(
            QtCore.QUrl.fromLocalFile(str(qml_dir / "MainMenu.qml"))
        )
        root = self.start_menu.rootObject()
        if root is not None:
            root.setProperty("theme", self.theme)
            root.setProperty("scale", 1.0)
            root.hostGame.connect(self._host_menu)
            root.joinGame.connect(self._join_menu)
            root.settings.connect(self._settings_dialog)
        self.menu_root = root
        self._transition_to(self.start_menu)

    def _host_menu(self) -> None:
        dialog = HostJoinDialog("host", self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                port = int(dialog.port_edit.text())
                max_players = int(dialog.max_players_edit.text())
            except ValueError:
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid settings")
                return
            cert = dialog.cert_edit.text().strip() or None
            key = dialog.key_edit.text().strip() or None
            self._start_host(port, max_players, cert, key)

    def _join_menu(self) -> None:
        dialog = HostJoinDialog("join", self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            token = dialog.token_edit.text().strip()
            if token:
                try:
                    addr, port, code = parse_join_token(token)
                except InvalidToken:
                    QtWidgets.QMessageBox.critical(self, "Error", "Invalid token")
                    return
            else:
                addr = dialog.addr_edit.text().strip()
                code = dialog.code_edit.text().strip()
                try:
                    port = int(dialog.port_edit.text())
                except ValueError:
                    QtWidgets.QMessageBox.critical(self, "Error", "Invalid port")
                    return
            cafile = dialog.cafile_edit.text().strip() or None
            self._start_join(addr, port, code, cafile)

    def _settings_dialog(self) -> None:
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QtWidgets.QFormLayout(dialog)
        theme_combo = QtWidgets.QComboBox()
        theme_combo.addItems(["light", "dark"])
        theme_combo.setCurrentText(self.theme)
        layout.addRow("Theme:", theme_combo)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.theme = theme_combo.currentText()
            os.environ["BANG_THEME"] = self.theme
            self.setStyleSheet(get_stylesheet(self.theme))
            if self.menu_root is not None:
                self.menu_root.setProperty("theme", self.theme)
            if hasattr(self, "game_root") and self.game_root is not None:
                self.game_root.setProperty("theme", self.theme)

    # Game view --------------------------------------------------------
    def _build_game_view(self) -> None:
        self.game_view = GameView(self.theme)
        self.game_view.action_signal.connect(self._send_action)
        self.game_view.end_turn_signal.connect(self._end_turn)
        self.hand_layout = self.game_view.hand_layout
        self.game_root = self.game_view.root_obj
        self._transition_to(self.game_view)

    # Networking -------------------------------------------------------
    def _start_host(
        self,
        port: int,
        max_players: int,
        certfile: str | None = None,
        keyfile: str | None = None,
    ) -> None:
        name = self._get_player_name()
        if not name:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please enter a valid name"
            )
            return
        room_code = secrets.token_hex(3)
        self.server_thread = ServerThread(
            "",
            port,
            room_code,
            [],
            max_players,
            certfile,
            keyfile,
        )
        self.server_thread.start()
        scheme = "wss" if certfile else "ws"
        uri = f"{scheme}://localhost:{port}"
        self._start_client(uri, room_code, cafile=certfile)
        self.setWindowTitle(f"Bang! - {room_code}")

    def _start_join(
        self, addr: str, port: int, code: str, cafile: str | None = None
    ) -> None:
        name = self._get_player_name()
        if not name:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please enter a valid name"
            )
            return
        scheme = "wss" if cafile else "ws"
        uri = f"{scheme}://{addr}:{port}"
        self._start_client(uri, code, cafile)

    def _start_client(self, uri: str, code: str, cafile: str | None = None) -> None:
        self.room_code = code
        self.client = ClientThread(
            uri,
            code,
            self._get_player_name(),
            cafile,
        )
        self.client.message_received.connect(self._append_message)
        self.client.start()
        self.local_name = self._get_player_name()
        self._build_game_view()

    def _append_message(self, msg: str) -> None:
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            if hasattr(self, "game_root") and self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                self.game_root.setProperty("logText", cur + msg + "\n")
            return

        if isinstance(data, dict):
            if "message" in data:
                if hasattr(self, "game_root") and self.game_root is not None:
                    cur = self.game_root.property("logText") or ""
                    self.game_root.setProperty(
                        "logText", cur + str(data["message"]) + "\n"
                    )
            if "players" in data:
                self._update_players(data["players"])
            if "hand" in data:
                self._update_hand(data["hand"])
            if "prompt" in data:
                self._show_prompt(data["prompt"], data)
        else:
            if hasattr(self, "game_root") and self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                self.game_root.setProperty("logText", cur + str(data) + "\n")

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
            if hasattr(self, "game_root") and self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                self.game_root.setProperty("logText", cur + f"Prompt: {prompt}\n")

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
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    ui = BangUI()
    ui.showMaximized()
    if os.getenv("BANG_AUTO_CLOSE"):
        QtCore.QTimer.singleShot(100, ui.close)
    app.exec()


if __name__ == "__main__":
    main()
