import asyncio
import json
import logging
import math
import secrets
from pathlib import Path
import os

from PySide6 import QtCore, QtGui, QtWidgets
import websockets
from websockets import WebSocketException

if __package__ in {None, ""}:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "bang_py"

from .network.server import BangServer


class ServerThread(QtCore.QThread):
    """Run a :class:`BangServer` in a background thread."""

    def __init__(self, host: str, port: int, room_code: str,
                 expansions: list[str], max_players: int) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.room_code = room_code
        self.expansions = expansions
        self.max_players = max_players
        self.loop = asyncio.new_event_loop()
        self.server_task: asyncio.Task | None = None

    def run(self) -> None:  # type: ignore[override]
        asyncio.set_event_loop(self.loop)
        server = BangServer(self.host, self.port, self.room_code,
                            self.expansions, self.max_players)
        self.server_task = self.loop.create_task(server.start())
        try:
            self.loop.run_until_complete(self.server_task)
        except asyncio.CancelledError:
            logging.info("Server thread cancelled")
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def stop(self) -> None:
        if self.server_task and not self.server_task.done():
            self.loop.call_soon_threadsafe(self.server_task.cancel)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


class ClientThread(QtCore.QThread):
    """Manage a websocket client connection in a background thread."""

    message_received = QtCore.Signal(str)

    def __init__(self, uri: str, room_code: str, name: str) -> None:
        super().__init__()
        self.uri = uri
        self.room_code = room_code
        self.name = name
        self.loop = asyncio.new_event_loop()
        self.websocket: websockets.WebSocketClientProtocol | None = None

    def run(self) -> None:  # type: ignore[override]
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())
        self.loop.close()

    def stop(self) -> None:
        if self.websocket and not self.websocket.closed:
            fut = asyncio.run_coroutine_threadsafe(self.websocket.close(),
                                                   self.loop)
            try:
                fut.result(timeout=1)
            except Exception as exc:  # noqa: BLE001
                logging.exception("Failed to close websocket: %s", exc)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    async def _run(self) -> None:
        try:
            self.websocket = await websockets.connect(self.uri)
            await self.websocket.recv()
            await self.websocket.send(self.room_code)
            response = await self.websocket.recv()
            if response != "Enter your name:":
                self.message_received.emit(response)
                return
            await self.websocket.send(self.name)
            join_msg = await self.websocket.recv()
            self.message_received.emit(join_msg)
            async for message in self.websocket:
                self.message_received.emit(message)
        except (OSError, WebSocketException) as exc:
            logging.exception("Connection error: %s", exc)
            self.message_received.emit(f"Connection error: {exc}")
        finally:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None

    def send_end_turn(self) -> None:
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send("end_turn"), self.loop)

    def send_json(self, payload: dict) -> None:
        """Serialize ``payload`` and send it to the server."""
        if self.loop.is_running():
            msg = json.dumps(payload)
            asyncio.run_coroutine_threadsafe(self._send(msg), self.loop)

    async def _send(self, msg: str) -> None:
        if not self.websocket or self.websocket.closed:
            self.message_received.emit("Send error: not connected")
            return
        try:
            await self.websocket.send(msg)
        except WebSocketException as exc:
            logging.exception("Send error: %s", exc)
            self.message_received.emit(f"Send error: {exc}")


class GameBoard(QtWidgets.QGraphicsView):
    """Simple board rendering using QGraphicsView."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)
        screen = QtGui.QGuiApplication.primaryScreen()
        if screen is not None:
            geom = screen.availableGeometry()
            self.max_width = geom.width()
            self.max_height = geom.height()
        else:
            self.max_width = 800
            self.max_height = 600
        self.card_width = 60
        self.card_height = 90
        self.card_pixmap = self._create_card_pixmap()
        self.players: list[dict] = []
        self._draw_board()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # noqa: D401
        """Handle widget resize and scale contents."""
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def _create_card_pixmap(self, width: int | None = None,
                             height: int | None = None) -> QtGui.QPixmap:
        w = width or self.card_width
        h = height or self.card_height
        pix = QtGui.QPixmap(w, h)
        pix.fill(QtGui.QColor("#ddd"))
        painter = QtGui.QPainter(pix)
        pen = QtGui.QPen(QtGui.QColor("#222"))
        painter.setPen(pen)
        painter.drawRect(0, 0, w - 1, h - 1)
        painter.end()
        return pix

    def _draw_board(self) -> None:
        self._scene.clear()
        self._scene.setSceneRect(0, 0, self.max_width, self.max_height)
        table = self._scene.addEllipse(5, 5, self.max_width - 10,
                                       self.max_height - 10,
                                       QtGui.QPen(),
                                       QtGui.QBrush(QtGui.QColor("forestgreen")))
        table.setZValue(-1)
        draw_x = self.max_width * 0.3
        draw_y = self.max_height * 0.5
        discard_x = self.max_width * 0.7
        self._scene.addPixmap(self.card_pixmap).setPos(draw_x, draw_y)
        self._scene.addText("Draw").setPos(draw_x, draw_y + self.card_height)
        self._scene.addPixmap(self.card_pixmap).setPos(discard_x, draw_y)
        self._scene.addText("Discard").setPos(discard_x,
                                              draw_y + self.card_height)

        if self.players:
            angle_step = 360 / len(self.players)
            center_x = self.max_width / 2
            center_y = self.max_height / 2
            radius = min(self.max_width, self.max_height) * 0.35
            for i, pl in enumerate(self.players):
                ang = math.radians(i * angle_step)
                x = center_x + radius * math.cos(ang) - self.card_width / 2
                y = center_y + radius * math.sin(ang) - self.card_height / 2
                self._scene.addPixmap(self.card_pixmap).setPos(x, y)
                text = f"{pl['name']} ({pl['health']})"
                self._scene.addText(text).setPos(x, y + self.card_height)

    def update_players(self, players: list[dict]) -> None:
        """Redraw the board to show ``players``."""
        self.players = players
        self._draw_board()


class CardButton(QtWidgets.QPushButton):
    """Button widget representing a hand card."""

    action_signal = QtCore.Signal(str, int)

    def __init__(self, text: str, index: int) -> None:
        super().__init__(text)
        self.index = index
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.clicked.connect(self._play)

    def _play(self) -> None:
        self.action_signal.emit("play_card", self.index)

    def _context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        discard = menu.addAction("Discard")
        chosen = menu.exec(self.mapToGlobal(pos))
        if chosen == discard:
            self.action_signal.emit("discard", self.index)


class BangUI(QtWidgets.QMainWindow):
    """Qt GUI for hosting, joining and playing a Bang game."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bang!")
        self.resize(1024, 768)
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.client: ClientThread | None = None
        self.server_thread: ServerThread | None = None
        self.room_code = ""

        self._build_start_menu()
        self._create_log_dock()

    # Menu screens -----------------------------------------------------
    def _build_start_menu(self) -> None:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        form = QtWidgets.QFormLayout()
        self.name_edit = QtWidgets.QLineEdit()
        form.addRow("Name:", self.name_edit)
        layout.addLayout(form)

        host_btn = QtWidgets.QPushButton("Host Game")
        host_btn.clicked.connect(self._host_menu)
        join_btn = QtWidgets.QPushButton("Join Game")
        join_btn.clicked.connect(self._join_menu)
        settings_btn = QtWidgets.QPushButton("Settings")
        settings_btn.clicked.connect(self._settings_dialog)

        layout.addWidget(host_btn)
        layout.addWidget(join_btn)
        layout.addWidget(settings_btn)
        layout.addStretch(1)

        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def _host_menu(self) -> None:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        self.port_edit = QtWidgets.QLineEdit("8765")
        self.max_players_edit = QtWidgets.QLineEdit("7")
        layout.addRow("Host Port:", self.port_edit)
        layout.addRow("Max Players:", self.max_players_edit)
        start_btn = QtWidgets.QPushButton("Start")
        start_btn.clicked.connect(self._start_host)
        layout.addRow(start_btn)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def _join_menu(self) -> None:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        self.addr_edit = QtWidgets.QLineEdit("localhost")
        self.join_port_edit = QtWidgets.QLineEdit("8765")
        self.code_edit = QtWidgets.QLineEdit()
        layout.addRow("Host Address:", self.addr_edit)
        layout.addRow("Port:", self.join_port_edit)
        layout.addRow("Room Code:", self.code_edit)
        join_btn = QtWidgets.QPushButton("Join")
        join_btn.clicked.connect(self._start_join)
        layout.addRow(join_btn)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def _settings_dialog(self) -> None:
        QtWidgets.QMessageBox.information(self, "Settings",
                                          "Settings dialog placeholder")

    # Game view --------------------------------------------------------
    def _build_game_view(self) -> None:
        widget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(widget)

        hbox = QtWidgets.QHBoxLayout()
        self.board = GameBoard()
        hbox.addWidget(self.board, 1)
        self.player_list = QtWidgets.QListWidget()
        self.player_list.setMaximumWidth(200)
        hbox.addWidget(self.player_list)
        vbox.addLayout(hbox, 1)

        self.hand_widget = QtWidgets.QWidget()
        self.hand_layout = QtWidgets.QHBoxLayout(self.hand_widget)
        vbox.addWidget(self.hand_widget)

        btn_draw = QtWidgets.QPushButton("Draw")
        btn_draw.clicked.connect(lambda: self._send_action({"action": "draw"}))
        vbox.addWidget(btn_draw)

        btn_end = QtWidgets.QPushButton("End Turn")
        btn_end.clicked.connect(self._end_turn)
        vbox.addWidget(btn_end)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def _create_log_dock(self) -> None:
        self.log_dock = QtWidgets.QDockWidget("Log", self)
        self.log_dock.setFloating(True)
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_dock.setWidget(self.log_text)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.log_dock)
        self.log_dock.hide()

    # Networking -------------------------------------------------------
    def _start_host(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Please enter your name")
            return
        port = int(self.port_edit.text())
        max_players = int(self.max_players_edit.text())
        room_code = secrets.token_hex(3)
        self.server_thread = ServerThread("", port, room_code, [], max_players)
        self.server_thread.start()
        uri = f"ws://localhost:{port}"
        self._start_client(uri, room_code)
        self.setWindowTitle(f"Bang! - {room_code}")

    def _start_join(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Please enter your name")
            return
        addr = self.addr_edit.text().strip()
        port = int(self.join_port_edit.text())
        code = self.code_edit.text().strip()
        uri = f"ws://{addr}:{port}"
        self._start_client(uri, code)

    def _start_client(self, uri: str, code: str) -> None:
        self.room_code = code
        self.client = ClientThread(uri, code, self.name_edit.text().strip())
        self.client.message_received.connect(self._append_message)
        self.client.start()
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
        if hasattr(self, "player_list"):
            self.player_list.clear()
            for p in players:
                self.player_list.addItem(f"{p['name']} ({p['health']})")
        if hasattr(self, "board"):
            self.board.update_players(players)

    def _update_hand(self, cards: list[str]) -> None:
        if not hasattr(self, "hand_layout"):
            return
        while self.hand_layout.count():
            item = self.hand_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for idx, name in enumerate(cards):
            btn = CardButton(name, idx)
            btn.action_signal.connect(self._handle_card_action)
            self.hand_layout.addWidget(btn)

    def _handle_card_action(self, action: str, index: int) -> None:
        if action == "play_card":
            self._send_action({"action": "play_card", "card_index": index})
        elif action == "discard":
            self._send_action({"action": "discard", "card_index": index})

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

