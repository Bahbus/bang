from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import random

from .deck import Deck
from .cards.card import Card
from .characters import BartCassidy, JesseJones

from .player import Player, Role


@dataclass
class GameManager:
    players: List[Player] = field(default_factory=list)
    deck: Deck = field(default_factory=Deck)
    discard_pile: List[Card] = field(default_factory=list)
    current_turn: int = 0
    turn_order: List[int] = field(default_factory=list)

    # Event listeners
    player_damaged_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    player_healed_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    turn_started_listeners: List[Callable[[Player], None]] = field(default_factory=list)

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def start_game(self) -> None:
        self.turn_order = list(range(len(self.players)))
        self.current_turn = 0
        # Deal initial hands
        for _ in range(2):
            for player in self.players:
                self.draw_card(player)
        self._begin_turn()

    def _begin_turn(self) -> None:
        if not self.turn_order:
            return
        idx = self.turn_order[self.current_turn]
        player = self.players[idx]
        self.draw_phase(player)
        for cb in self.turn_started_listeners:
            cb(player)

    def end_turn(self) -> None:
        if not self.turn_order:
            return
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        self._begin_turn()

    def draw_card(self, player: Player, num: int = 1) -> None:
        for _ in range(num):
            card = self.deck.draw()
            if card is None:
                if self.discard_pile:
                    # reshuffle discard into deck
                    self.deck.cards.extend(self.discard_pile)
                    self.discard_pile.clear()
                    random.shuffle(self.deck.cards)
                    card = self.deck.draw()
            if card:
                player.hand.append(card)

    def draw_phase(self, player: Player) -> None:
        if isinstance(player.character, JesseJones):
            opponents = [p for p in self.players if p is not player and p.hand]
            if opponents:
                source = random.choice(opponents)
                card = source.hand.pop()
                player.hand.append(card)
                self.draw_card(player)
                return
        self.draw_card(player, 2)

    def play_card(self, player: Player, card: Card, target: Optional[Player] = None) -> None:
        if card not in player.hand:
            return
        player.hand.remove(card)
        before = target.health if target else None
        card.play(target)
        if target and before is not None and target.health < before:
            self.on_player_damaged(target)
        if target and before is not None and target.health > before:
            self.on_player_healed(target)
        self.discard_pile.append(card)

    def discard_card(self, player: Player, card: Card) -> None:
        if card in player.hand:
            player.hand.remove(card)
            self.discard_pile.append(card)

    def _get_player_by_index(self, idx: int) -> Optional[Player]:
        if 0 <= idx < len(self.players):
            return self.players[idx]
        return None

    def on_player_damaged(self, player: Player) -> None:
        for cb in self.player_damaged_listeners:
            cb(player)
        if player.character and player.character.__class__.__name__ == "BartCassidy":
            self.draw_card(player)
        if player.health <= 0:
            self._check_win_conditions()

    def on_player_healed(self, player: Player) -> None:
        for cb in self.player_healed_listeners:
            cb(player)

    def _check_win_conditions(self) -> None:
        alive = [p for p in self.players if p.is_alive()]
        self.turn_order = [i for i in self.turn_order if self.players[i].is_alive()]
        sheriff_alive = any(p.role == Role.SHERIFF for p in alive)
        outlaws_alive = any(p.role == Role.OUTLAW for p in alive)
        renegade_alive = any(p.role == Role.RENEGADE for p in alive)

        if not sheriff_alive:
            if len(alive) == 1 and alive[0].role == Role.RENEGADE:
                print("Renegade wins!")
            else:
                print("Outlaws win!")
        elif not outlaws_alive and not renegade_alive:
            print("Sheriff and Deputies win!")

