from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import random

from .deck import Deck
from .deck_factory import create_standard_deck
from .cards.card import Card
from .characters import (
    BartCassidy,
    BlackJack,
    CalamityJanet,
    ElGringo,
    JesseJones,
    Jourdonnais,
    KitCarlson,
    LuckyDuke,
    PedroRamirez,
    SidKetchum,
    SuzyLafayette,
    VultureSam,
    WillyTheKid,
)
from .cards.bang import BangCard
from .cards.missed import MissedCard

from .player import Player, Role


@dataclass
class GameManager:
    """Manage players, deck and discard pile while controlling turn order and
    triggering game events."""
    players: List[Player] = field(default_factory=list)
    deck: Deck = field(default_factory=create_standard_deck)
    discard_pile: List[Card] = field(default_factory=list)
    current_turn: int = 0
    turn_order: List[int] = field(default_factory=list)

    # Event listeners
    player_damaged_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    player_healed_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    turn_started_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    game_over_listeners: List[Callable[[str], None]] = field(default_factory=list)

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
        player.metadata["bangs_played"] = 0
        for cb in self.turn_started_listeners:
            cb(player)

    def end_turn(self) -> None:
        if not self.turn_order:
            return
        idx = self.turn_order[self.current_turn]
        self.discard_phase(self.players[idx])
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
        char = player.character
        if isinstance(char, JesseJones):
            opponents = [p for p in self.players if p is not player and p.hand]
            if opponents:
                source = random.choice(opponents)
                card = source.hand.pop()
                player.hand.append(card)
                self.draw_card(player)
                return
        if isinstance(char, BlackJack):
            first = self.deck.draw()
            if first:
                player.hand.append(first)
            second = self.deck.draw()
            if second:
                player.hand.append(second)
                if getattr(second, "suit", None) in ("Hearts", "Diamonds"):
                    self.draw_card(player)
            return
        if isinstance(char, KitCarlson):
            cards = [self.deck.draw(), self.deck.draw(), self.deck.draw()]
            keep = [c for c in cards if c][:2]
            for c in keep:
                player.hand.append(c)
            discard = next((c for c in cards if c and c not in keep), None)
            if discard:
                self.discard_pile.append(discard)
            return
        if isinstance(char, PedroRamirez) and self.discard_pile:
            player.hand.append(self.discard_pile.pop())
            self.draw_card(player)
            return
        self.draw_card(player, 2)

    def discard_phase(self, player: Player) -> None:
        """Discard down to the player's hand limit at the end of their turn."""
        limit = player.health
        while len(player.hand) > limit:
            card = player.hand.pop()
            self.discard_pile.append(card)

    def play_card(self, player: Player, card: Card, target: Optional[Player] = None) -> None:
        if card not in player.hand:
            return
        # Determine if this card counts as a Bang!
        is_bang = isinstance(card, BangCard) or (
            isinstance(player.character, CalamityJanet) and isinstance(card, MissedCard) and target
        )
        if is_bang:
            count = int(player.metadata.get("bangs_played", 0))
            gun = player.equipment.get("Gun")
            unlimited = isinstance(player.character, WillyTheKid) or getattr(gun, "unlimited_bang", False)
            if count >= 1 and not unlimited:
                # Cannot play more Bang! cards this turn
                return
        player.hand.remove(card)
        before = target.health if target else None
        if isinstance(player.character, CalamityJanet) and isinstance(card, MissedCard) and target:
            BangCard().play(target, self.deck)
        else:
            if isinstance(card, BangCard):
                card.play(target, self.deck)
            else:
                card.play(target)
        if target and before is not None and target.health < before:
            self.on_player_damaged(target, player)
        if target and before is not None and target.health > before:
            self.on_player_healed(target)
        self.discard_pile.append(card)
        if is_bang:
            player.metadata["bangs_played"] = int(player.metadata.get("bangs_played", 0)) + 1
        if isinstance(player.character, SuzyLafayette) and not player.hand:
            self.draw_card(player)

    def discard_card(self, player: Player, card: Card) -> None:
        if card in player.hand:
            player.hand.remove(card)
            self.discard_pile.append(card)
            if isinstance(player.character, SuzyLafayette) and not player.hand:
                self.draw_card(player)

    def sid_ketchum_ability(self, player: Player) -> None:
        if not isinstance(player.character, SidKetchum):
            return
        if len(player.hand) < 2 or player.health >= player.max_health:
            return
        for _ in range(2):
            card = player.hand.pop()
            self.discard_pile.append(card)
        player.heal(1)
        self.on_player_healed(player)

    def _get_player_by_index(self, idx: int) -> Optional[Player]:
        if 0 <= idx < len(self.players):
            return self.players[idx]
        return None

    def on_player_damaged(self, player: Player, source: Optional[Player] = None) -> None:
        for cb in self.player_damaged_listeners:
            cb(player)
        if isinstance(player.character, BartCassidy):
            self.draw_card(player)
        if isinstance(player.character, ElGringo) and source and source.hand:
            stolen = random.choice(source.hand)
            source.hand.remove(stolen)
            player.hand.append(stolen)
        if player.health <= 0:
            for p in self.players:
                if p is not player and isinstance(p.character, VultureSam):
                    p.hand.extend(player.hand)
                    player.hand.clear()
            result = self._check_win_conditions()

    def on_player_healed(self, player: Player) -> None:
        for cb in self.player_healed_listeners:
            cb(player)

    def _check_win_conditions(self) -> Optional[str]:
        alive = [p for p in self.players if p.is_alive()]
        self.turn_order = [i for i in self.turn_order if self.players[i].is_alive()]
        sheriff_alive = any(p.role == Role.SHERIFF for p in alive)
        outlaws_alive = any(p.role == Role.OUTLAW for p in alive)
        renegade_alive = any(p.role == Role.RENEGADE for p in alive)

        result = None
        if not sheriff_alive:
            if len(alive) == 1 and alive[0].role == Role.RENEGADE:
                result = "Renegade wins!"
            else:
                result = "Outlaws win!"
        elif not outlaws_alive and not renegade_alive:
            result = "Sheriff and Deputies win!"
        if result:
            for cb in self.game_over_listeners:
                cb(result)
        return result

