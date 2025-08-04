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
        play_sound: QtCore.QObject | None = None,
        click_sound: QtCore.QObject | None = None,
        discard_sound: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(text)
        self.index = index
        self.play_sound = play_sound
        self.click_sound = click_sound
        self.discard_sound = discard_sound
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.clicked.connect(self._play)

        self.set_card(text, card_type, rank, suit, card_set)

    def set_card(
        self,
        text: str,
        card_type: str = "action",
        rank: int | str | None = None,
        suit: str | None = None,
        card_set: str | None = None,
    ) -> None:
        """Update button appearance for a new card."""
        self.setText(text)
        loader = get_loader()
        pix = loader.compose_card(card_type, rank, suit, card_set, text)
        if not pix.isNull():
            self.setIcon(QtGui.QIcon(pix))
            self.setIconSize(QtCore.QSize(pix.width(), pix.height()))
            self.setText("")
        else:
            self.setIcon(QtGui.QIcon())

    def _play(self) -> None:
        if self.click_sound:
            self.click_sound.play()
        if self.play_sound:
            self.play_sound.play()
        self.action_signal.emit("play_card", self.index)

    def _context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        discard = menu.addAction("Discard")
        chosen = menu.exec(self.mapToGlobal(pos))
        if chosen == discard:
            if self.click_sound:
                self.click_sound.play()
            if self.discard_sound:
                self.discard_sound.play()
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
            self.root_obj.drawCard.connect(self._draw_card)
            self.root_obj.discardCard.connect(self._discard_card)
            self.root_obj.endTurn.connect(self._end_turn)
        vbox.addWidget(self.board_qml, 1)

        self.click_sound = load_sound("ui_click", self)
        self.draw_sound = load_sound("draw_card", self)
        self.discard_sound = load_sound("discard_card", self)
        self.shuffle_sound = load_sound("shuffle_cards", self)
        self.play_sound = load_sound("play_card", self)

        self.hand_widget = QtWidgets.QWidget()
        self.hand_layout = QtWidgets.QHBoxLayout(self.hand_widget)
        vbox.addWidget(self.hand_widget)
        self.hand_buttons: list[CardButton] = []

    def update_players(self, players: list[dict], self_name: str | None = None) -> None:
        if self.root_obj is not None:
            self.root_obj.setProperty("players", players)
            if self_name is not None:
                self.root_obj.setProperty("selfName", self_name)

    def update_hand(self, cards: list[object]) -> None:
        if self.shuffle_sound:
            self.shuffle_sound.play()

        # Ensure enough buttons exist and update their content
        for idx, card in enumerate(cards):
            if idx < len(self.hand_buttons):
                btn = self.hand_buttons[idx]
            else:
                btn = CardButton(
                    "",
                    idx,
                    play_sound=self.play_sound,
                    click_sound=self.click_sound,
                    discard_sound=self.discard_sound,
                )
                btn.action_signal.connect(self._forward_action)
                self.hand_buttons.append(btn)
                self.hand_layout.addWidget(btn)

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
            btn.index = idx
            btn.set_card(name, ctype, rank, suit, cset)
            btn.show()

        # Hide any extra buttons
        for extra in self.hand_buttons[len(cards):]:
            extra.hide()

    def _forward_action(self, act: str, index: int) -> None:
        """Relay button actions with card index."""
        self.action_signal.emit({"action": act, "card_index": index})

    def _draw_card(self) -> None:
        if self.click_sound:
            self.click_sound.play()
        if self.draw_sound:
            self.draw_sound.play()
        self.action_signal.emit({"action": "draw"})

    def _discard_card(self) -> None:
        if self.click_sound:
            self.click_sound.play()
        if self.discard_sound:
            self.discard_sound.play()
        self.action_signal.emit({"action": "discard"})

    def _end_turn(self) -> None:
        if self.click_sound:
            self.click_sound.play()
        self.end_turn_signal.emit()
