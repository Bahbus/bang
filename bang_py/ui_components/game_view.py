from __future__ import annotations

import base64
from importlib import resources

from PySide6 import QtCore, QtWidgets, QtQuickWidgets

from .card_images import get_loader


class GameView(QtWidgets.QWidget):
    """Main in-game widget showing the QML game board."""

    action_signal = QtCore.Signal(dict)
    end_turn_signal = QtCore.Signal()

    def __init__(self, theme: str = "light") -> None:
        super().__init__()
        self.theme = theme
        vbox = QtWidgets.QVBoxLayout(self)

        self.board_qml = QtQuickWidgets.QQuickWidget()
        self.board_qml.setResizeMode(
            QtQuickWidgets.QQuickWidget.SizeRootObjectToView
        )
        qml_dir = resources.files("bang_py") / "qml"
        with resources.as_file(qml_dir / "GameBoard.qml") as qml_path:
            self.board_qml.setSource(QtCore.QUrl.fromLocalFile(str(qml_path)))
        self.root_obj = self.board_qml.rootObject()
        if self.root_obj is not None:
            self.root_obj.setProperty("theme", theme)
            self.root_obj.setProperty("scale", 1.0)
            self.root_obj.drawCard.connect(self._draw_card)
            self.root_obj.discardCard.connect(self._discard_card)
            self.root_obj.endTurn.connect(self._end_turn)
            self.root_obj.playCard.connect(self._play_card)
            self.root_obj.discardFromHand.connect(self._discard_from_hand)
        vbox.addWidget(self.board_qml, 1)

    def update_players(self, players: list[dict], self_name: str | None = None) -> None:
        """Update player information on the board."""
        if self.root_obj is not None:
            self.root_obj.setProperty("players", players)
            if self_name is not None:
                self.root_obj.setProperty("selfName", self_name)

    def update_hand(self, cards: list[object]) -> None:
        """Refresh the hand shown on the board."""
        if self.root_obj is None:
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
                encoded = base64.b64encode(bytes(buffer.data())).decode("ascii")
                source = f"data:image/png;base64,{encoded}"
            else:
                source = ""
            hand.append({"name": name, "source": source})
        self.root_obj.setProperty("hand", hand)

    # Qt signal handlers ----------------------------------------------
    def _draw_card(self) -> None:
        self.action_signal.emit({"action": "draw"})

    def _discard_card(self) -> None:
        self.action_signal.emit({"action": "discard"})

    def _play_card(self, index: int) -> None:
        self.action_signal.emit({"action": "play_card", "card_index": int(index)})

    def _discard_from_hand(self, index: int) -> None:
        self.action_signal.emit({"action": "discard", "card_index": int(index)})

    def _end_turn(self) -> None:
        self.end_turn_signal.emit()
