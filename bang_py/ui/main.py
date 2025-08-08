"""Qt Quick based interface for the Bang card game."""

from __future__ import annotations

import json
import os
import secrets
from importlib import resources

from PySide6 import QtCore, QtWidgets, QtQuick

from .components import ClientThread, ServerThread
from .components.card_images import get_loader
from .theme import get_current_theme
from ..network.token_utils import parse_join_token
from ..network.validation import validate_player_name
from cryptography.fernet import InvalidToken

CHARACTER_ASSETS = resources.files("bang_py") / "assets" / "characters"


class BangUI(QtCore.QObject):
    """Interface controller backed by a QML scene."""

    def __init__(self, theme: str | None = None) -> None:
        super().__init__()
        self.theme = theme or get_current_theme()
        self.view = QtQuick.QQuickView()
        self.view.setResizeMode(QtQuick.QQuickView.SizeRootObjectToView)
        qml_dir = resources.files("bang_py.ui") / "qml"
        with resources.as_file(qml_dir / "Main.qml") as qml_path:
            self.view.setSource(QtCore.QUrl.fromLocalFile(str(qml_path)))
        self.root = self.view.rootObject()
        if self.root is not None:
            self.root.setProperty("theme", self.theme)
            self.root.hostRequested.connect(self._host_menu)
            self.root.joinRequested.connect(self._join_menu)
            self.root.settingsChanged.connect(self._settings_changed)
            self.root.drawCard.connect(lambda: self._send_action({"action": "draw"}))
            self.root.discardCard.connect(lambda: self._send_action({"action": "discard"}))
            self.root.endTurn.connect(self._end_turn)
            self.root.playCard.connect(
                lambda i: self._send_action({"action": "play_card", "card_index": int(i)})
            )
            self.root.discardFromHand.connect(
                lambda i: self._send_action({"action": "discard", "card_index": int(i)})
            )
        self.client: ClientThread | None = None
        self.server_thread: ServerThread | None = None
        self.room_code = ""
        self.local_name = ""
        self.game_root: QtCore.QObject | None = None

    # Menu callbacks --------------------------------------------------
    def _host_menu(
        self,
        name: str,
        port_text: str,
        max_players_text: str,
        cert: str,
        key: str,
    ) -> None:
        name = name.strip()
        if not validate_player_name(name):
            QtWidgets.QMessageBox.critical(None, "Error", "Please enter a valid name")
            return
        try:
            port = int(port_text)
            max_players = int(max_players_text)
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Error", "Invalid settings")
            return
        certfile = cert.strip() or None
        keyfile = key.strip() or None
        self.local_name = name
        self._start_host(port, max_players, certfile, keyfile)

    def _join_menu(
        self,
        name: str,
        addr: str,
        port_text: str,
        code: str,
        cafile: str,
    ) -> None:
        name = name.strip()
        if not validate_player_name(name):
            QtWidgets.QMessageBox.critical(None, "Error", "Please enter a valid name")
            return
        cafile_opt = cafile.strip() or None
        if not addr and port_text == "0":
            token = code.strip()
            if not token:
                QtWidgets.QMessageBox.critical(None, "Error", "Missing token")
                return
            try:
                addr, port, code = parse_join_token(token)
            except InvalidToken:
                QtWidgets.QMessageBox.critical(None, "Error", "Invalid token")
                return
        else:
            try:
                port = int(port_text)
            except ValueError:
                QtWidgets.QMessageBox.critical(None, "Error", "Invalid port")
                return
        self.local_name = name
        self._start_join(addr or "localhost", port, code.strip(), cafile_opt)

    def _settings_changed(self, theme: str) -> None:
        self.theme = theme
        os.environ["BANG_THEME"] = theme
        if self.root is not None:
            self.root.setProperty("theme", theme)
        if self.game_root is not None:
            self.game_root.setProperty("theme", theme)

    # Networking ------------------------------------------------------
    def _start_host(
        self,
        port: int,
        max_players: int,
        certfile: str | None = None,
        keyfile: str | None = None,
    ) -> None:
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

    def _start_join(self, addr: str, port: int, code: str, cafile: str | None = None) -> None:
        scheme = "wss" if cafile else "ws"
        uri = f"{scheme}://{addr}:{port}"
        self._start_client(uri, code, cafile)

    def _start_client(self, uri: str, code: str, cafile: str | None = None) -> None:
        self.room_code = code
        self.client = ClientThread(uri, code, self.local_name, cafile)
        self.client.message_received.connect(self._append_message)
        self.client.start()
        self._build_game_view()

    # QML interaction -------------------------------------------------
    def _build_game_view(self) -> None:
        if self.root is not None:
            QtCore.QMetaObject.invokeMethod(self.root, "showGame")
            self.game_root = self.root.property("gameBoardItem")
            if self.game_root is not None:
                self.game_root.setProperty("theme", self.theme)

    def _append_message(self, msg: str) -> None:
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            if self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                self.game_root.setProperty("logText", cur + msg + "\n")
            return

        if isinstance(data, dict):
            if "message" in data and self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                text = str(data["message"])
                self.game_root.setProperty("logText", cur + text + "\n")
                if "BangCard" in text:
                    QtCore.QMetaObject.invokeMethod(self.game_root, "playBang")
                if "GatlingCard" in text:
                    QtCore.QMetaObject.invokeMethod(self.game_root, "playManyBangs")
                if "IndiansCard" in text:
                    QtCore.QMetaObject.invokeMethod(self.game_root, "playIndians")
                if "MissedCard" in text:
                    QtCore.QMetaObject.invokeMethod(self.game_root, "playMissed")
            if "players" in data:
                self._update_players(data["players"])
            if "hand" in data:
                self._update_hand(data["hand"])
            if "prompt" in data:
                self._show_prompt(data["prompt"], data)
        else:
            if self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                self.game_root.setProperty("logText", cur + str(data) + "\n")

    def _end_turn(self) -> None:
        if self.client:
            self.client.send_end_turn()

    def _send_action(self, payload: dict) -> None:
        if self.client:
            self.client.send_json(payload)

    def _update_players(self, players: list[dict]) -> None:
        if self.game_root is None:
            return
        updated: list[dict[str, object]] = []
        for pl in players:
            portrait = ""
            character = pl.get("character", "")
            if character:
                slug = character.lower().replace(" ", "_")
                filename = f"{slug}.webp"
                if (CHARACTER_ASSETS / filename).is_file():
                    portrait = f"../assets/characters/{filename}"
            updated.append({**pl, "portrait": portrait})
        self.game_root.setProperty("players", updated)
        self.game_root.setProperty("selfName", self.local_name)

    def _update_hand(self, cards: list[object]) -> None:
        if self.game_root is None:
            return
        loader = get_loader()
        hand: list[dict[str, object]] = []
        for card in cards:
            if isinstance(card, str):
                name = card
                ctype = "action"
                rank = suit = cset = None
            else:
                name = getattr(card, "card_name", str(card))
                ctype = getattr(card, "card_type", "action")
                rank = getattr(card, "rank", None)
                suit = getattr(card, "suit", None)
                cset = getattr(card, "card_set", None)
            pix = loader.compose_card(ctype, rank, suit, cset, name)
            if not pix.isNull():
                buffer = QtCore.QBuffer()
                buffer.open(QtCore.QIODevice.WriteOnly)
                pix.save(buffer, "PNG")
                encoded = QtCore.QByteArray(buffer.data()).toBase64().data().decode()
                source = f"data:image/png;base64,{encoded}"
            else:
                source = ""
            hand.append({"name": name, "source": source})
        self.game_root.setProperty("hand", hand)

    def _show_prompt(self, prompt: str, data: dict) -> None:
        if prompt == "general_store":
            cards = data.get("cards", [])
            item, ok = QtWidgets.QInputDialog.getItem(
                None, "General Store", "Pick a card:", cards, 0, False
            )
            if ok:
                index = cards.index(item)
                self._send_action({"action": "general_store_pick", "index": index})
        elif "options" in data:
            opts = [o.get("name", str(i)) for i, o in enumerate(data["options"])]
            item, ok = QtWidgets.QInputDialog.getItem(
                None, prompt.replace("_", " ").title(), "Choose:", opts, 0, False
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
            if self.game_root is not None:
                cur = self.game_root.property("logText") or ""
                self.game_root.setProperty("logText", cur + f"Prompt: {prompt}\n")

    def show(self) -> None:
        self.view.setTitle("Bang!")
        self.view.show()

    def close(self) -> None:
        if self.client:
            self.client.stop()
            self.client.wait(1000)
            self.client = None
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait(1000)
            self.server_thread = None
        QtWidgets.QApplication.quit()


def main() -> None:
    """Launch the QML interface."""
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    ui = BangUI()
    ui.show()
    if os.getenv("BANG_AUTO_CLOSE"):
        QtCore.QTimer.singleShot(100, ui.close)
    app.exec()


if __name__ == "__main__":
    main()
