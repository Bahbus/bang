from __future__ import annotations

import math

from PySide6 import QtCore, QtGui, QtWidgets


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
        self.self_name: str | None = None
        self._draw_board()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # noqa: D401
        """Handle widget resize and scale contents."""
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def _create_card_pixmap(
        self, width: int | None = None, height: int | None = None
    ) -> QtGui.QPixmap:
        w = width or self.card_width
        h = height or self.card_height
        pix = QtGui.QPixmap(w, h)
        pix.fill(QtGui.QColor("#f4e1b5"))
        painter = QtGui.QPainter(pix)
        pen = QtGui.QPen(QtGui.QColor("#8b4513"))
        painter.setPen(pen)
        painter.drawRect(0, 0, w - 1, h - 1)
        painter.end()
        return pix

    def _draw_board(self) -> None:
        self._scene.clear()
        self._scene.setSceneRect(0, 0, self.max_width, self.max_height)
        table = self._scene.addEllipse(
            5,
            5,
            self.max_width - 10,
            self.max_height - 10,
            QtGui.QPen(),
            QtGui.QBrush(QtGui.QColor("saddlebrown")),
        )
        table.setZValue(-1)
        center_x = self.max_width / 2
        draw_x = center_x - self.card_width * 1.5
        draw_y = self.max_height * 0.5
        discard_x = center_x + self.card_width * 0.5
        self._scene.addPixmap(self.card_pixmap).setPos(draw_x, draw_y)
        self._scene.addText("Draw").setPos(draw_x, draw_y + self.card_height)
        self._scene.addPixmap(self.card_pixmap).setPos(discard_x, draw_y)
        self._scene.addText("Discard").setPos(
            discard_x, draw_y + self.card_height
        )

        # Star emblem at the center of the table
        star = QtGui.QPolygonF()
        outer = 15
        inner = 6
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = outer if i % 2 == 0 else inner
            star.append(QtCore.QPointF(r * math.cos(angle), r * math.sin(angle)))
        item = self._scene.addPolygon(
            star,
            QtGui.QPen(QtGui.QColor("gold")),
            QtGui.QBrush(QtGui.QColor("gold")),
        )
        item.setPos(center_x, self.max_height / 2)

        if self.players:
            angle_step = 360 / len(self.players)
            center_y = self.max_height / 2
            radius = min(self.max_width, self.max_height) * 0.35
            idx = next(
                (i for i, pl in enumerate(self.players) if pl["name"] == self.self_name),
                0,
            )
            for i, pl in enumerate(self.players):
                ang = math.radians((i - idx) * angle_step + 90)
                x = center_x + radius * math.cos(ang) - self.card_width / 2
                y = center_y + radius * math.sin(ang) - self.card_height / 2
                self._scene.addPixmap(self.card_pixmap).setPos(x, y)
                text = f"{pl['name']} ({pl['health']})"
                self._scene.addText(text).setPos(x, y + self.card_height)

    def update_players(self, players: list[dict], self_name: str | None = None) -> None:
        """Redraw the board to show ``players`` with ``self_name`` at the bottom."""
        self.players = players
        self.self_name = self_name
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


class GameView(QtWidgets.QWidget):
    """Main in-game widget showing board and hand."""

    action_signal = QtCore.Signal(dict)
    end_turn_signal = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        vbox = QtWidgets.QVBoxLayout(self)

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
        btn_draw.clicked.connect(lambda: self.action_signal.emit({"action": "draw"}))
        vbox.addWidget(btn_draw)

        btn_end = QtWidgets.QPushButton("End Turn")
        btn_end.clicked.connect(self.end_turn_signal.emit)
        vbox.addWidget(btn_end)

    def update_players(self, players: list[dict], self_name: str | None = None) -> None:
        self.player_list.clear()
        for p in players:
            self.player_list.addItem(f"{p['name']} ({p['health']})")
        self.board.update_players(players, self_name)

    def update_hand(self, cards: list[str]) -> None:
        while self.hand_layout.count():
            item = self.hand_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for idx, name in enumerate(cards):
            btn = CardButton(name, idx)
            btn.action_signal.connect(
                lambda act, i=idx: self.action_signal.emit({
                    "action": act,
                    "card_index": i,
                })
            )
            self.hand_layout.addWidget(btn)
