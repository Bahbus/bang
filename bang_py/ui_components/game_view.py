from __future__ import annotations

import math
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from .card_images import card_image_loader

ASSETS_DIR = Path(__file__).resolve().with_name("assets")
BULLET_PATH = ASSETS_DIR / "bullet.png"


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
        self.bullet_pixmap = QtGui.QPixmap(str(BULLET_PATH)).scaled(
            20,
            10,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
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
        return card_image_loader.get_template("brown").scaled(
            w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )

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

                bullet_y = y + self.card_height
                spacing = 2
                health = int(pl.get("health", 0))
                bullet_w = self.bullet_pixmap.width()
                row_w = health * bullet_w + max(0, health - 1) * spacing
                start_x = x + (self.card_width - row_w) / 2
                for b in range(health):
                    item = self._scene.addPixmap(self.bullet_pixmap)
                    item.setPos(start_x + b * (bullet_w + spacing), bullet_y)

                name_item = self._scene.addText(pl["name"])
                name_item.setPos(x, bullet_y + self.bullet_pixmap.height() + 2)
                name_item.setToolTip(f"Health: {health}")

    def update_players(self, players: list[dict], self_name: str | None = None) -> None:
        """Redraw the board to show ``players`` with ``self_name`` at the bottom."""
        self.players = players
        self.self_name = self_name
        self._draw_board()


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

        pix = card_image_loader.compose_card(card_type, rank, suit, card_set)
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
            item = QtWidgets.QListWidgetItem()
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            name_label = QtWidgets.QLabel(p["name"])
            layout.addWidget(name_label)
            bullet_layout = QtWidgets.QHBoxLayout()
            bullet_layout.setSpacing(2)
            for _ in range(int(p.get("health", 0))):
                lbl = QtWidgets.QLabel()
                lbl.setPixmap(self.board.bullet_pixmap)
                bullet_layout.addWidget(lbl)
            layout.addLayout(bullet_layout)
            layout.addStretch(1)
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            item.setToolTip(f"Health: {p.get('health', 0)}")
            self.player_list.addItem(item)
            self.player_list.setItemWidget(item, widget)
        self.board.update_players(players, self_name)

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
