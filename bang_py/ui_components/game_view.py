from __future__ import annotations

from importlib import resources

from PySide6 import QtCore, QtGui, QtWidgets, QtQuickWidgets

from .card_images import get_loader, load_sound


class CardButton(QtWidgets.QPushButton):
    """Button widget representing a hand card."""

    action_signal = QtCore.Signal(str, int)

    def __init__(
        self,
        text: str,
        index: int,
        card_type: str = "action",
        rank: int | str | None = None,
        suit: str | None = None,
        card_set: str | None = None,
    ) -> None:
        super().__init__(text)
        self.index = index
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.clicked.connect(self._play)

        loader = get_loader()
        pix = loader.compose_card(card_type, rank, suit, card_set)
        if not pix.isNull():
            self.setIcon(QtGui.QIcon(pix))
            self.setIconSize(QtCore.QSize(pix.width(), pix.height()))
            self.setText("")

    def _play(self) -> None:
        self.action_signal.emit("play_card", self.index)

    def _context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        discard = menu.addAction("Discard")
        chosen = menu.exec(self.mapToGlobal(pos))
        if chosen == discard:
            self.action_signal.emit("discard", self.index)


class GameView(QtWidgets.QWidget):
    """Main in-game widget showing board and hand."""

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
            self.root_obj.drawCard.connect(
                lambda: self.action_signal.emit({"action": "draw"})
            )
            self.root_obj.discardCard.connect(
                lambda: self.action_signal.emit({"action": "discard"})
            )
            self.root_obj.endTurn.connect(self.end_turn_signal.emit)
        vbox.addWidget(self.board_qml, 1)

        self.update_sound = load_sound("beep")

        self.hand_widget = QtWidgets.QWidget()
        self.hand_layout = QtWidgets.QHBoxLayout(self.hand_widget)
        vbox.addWidget(self.hand_widget)

    def update_players(self, players: list[dict], self_name: str | None = None) -> None:
        if self.update_sound:
            self.update_sound.play()
        if self.root_obj is not None:
            self.root_obj.setProperty("players", players)
            if self_name is not None:
                self.root_obj.setProperty("selfName", self_name)

    def update_hand(self, cards: list[object]) -> None:
        while self.hand_layout.count():
            item = self.hand_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for idx, card in enumerate(cards):
            if isinstance(card, str):
                name = card
                ctype = "action"
                rank = None
                suit = None
                cset = None
            else:
                name = getattr(card, "card_name", str(card))
                ctype = getattr(card, "card_type", "action")
                rank = getattr(card, "rank", None)
                suit = getattr(card, "suit", None)
                cset = getattr(card, "card_set", None)
            btn = CardButton(name, idx, ctype, rank, suit, cset)
            btn.action_signal.connect(
                lambda act, i=idx: self.action_signal.emit({
                    "action": act,
                    "card_index": i,
                })
            )
            self.hand_layout.addWidget(btn)
