"""Draw phase helpers for :class:`GameManager`."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
import random
from collections import deque

from ..cards.card import BaseCard
from ..game_manager_protocol import GameManagerProtocol

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..player import Player


class DrawPhaseMixin:
    """Provide draw phase logic for :class:`GameManager`."""

    deck: object
    discard_pile: list[BaseCard]
    event_flags: dict
    _players: list["Player"]
    turn_order: list[int]
    current_turn: int
    phase: str
    draw_phase_listeners: list
    play_phase_listeners: list
    turn_started_listeners: list

    # ------------------------------------------------------------------
    # Deck helpers
    def _draw_from_deck(self) -> BaseCard | None:
        """Draw a card reshuffling the discard pile if needed."""
        if self.deck is None:
            return None
        card = self.deck.draw()
        if card is None and self.discard_pile:
            self.deck.cards.extend(self.discard_pile)
            self.discard_pile.clear()
            cards = list(self.deck.cards)
            random.shuffle(cards)
            self.deck.cards = deque(cards)
            card = self.deck.draw()
        return card

    def draw_card(self, player: "Player", num: int = 1) -> None:
        """Draw ``num`` cards for ``player`` applying event modifiers."""
        bonus = int(self.event_flags.get("peyote_bonus", 0))
        for _ in range(num + bonus):
            card: BaseCard | None
            if self.event_flags.get("abandoned_mine") and self.discard_pile:
                card = self.discard_pile.pop()
            else:
                card = self._draw_from_deck()
            if card:
                suit = self.event_flags.get("suit_override")
                if suit:
                    card.suit = suit
                player.hand.append(card)

    # ------------------------------------------------------------------
    # Draw phase
    def draw_phase(
        self,
        player: "Player",
        *,
        jesse_target: "Player" | None = None,
        jesse_card: int | None = None,
        kit_back: int | None = None,
        pedro_use_discard: bool | None = None,
        jose_equipment: int | None = None,
        pat_target: "Player" | None = None,
        pat_card: str | None = None,
        skip_heal: bool | None = None,
        peyote_guesses: list[str] | None = None,
        ranch_discards: list[int] | None = None,
        handcuffs_suit: str | None = None,
        blood_target: "Player" | None = None,
    ) -> None:
        """Execute the draw phase for ``player``."""
        if self._draw_pre_checks(player, skip_heal=skip_heal, blood_target=blood_target):
            return

        if self._dispatch_draw_listeners(
            player,
            jesse_target=jesse_target,
            jesse_card=jesse_card,
            kit_back=kit_back,
            pedro_use_discard=pedro_use_discard,
            jose_equipment=jose_equipment,
            pat_target=pat_target,
            pat_card=pat_card,
        ):
            return

        self._perform_draw(player, peyote_guesses)
        self._post_draw_events(
            player,
            ranch_discards=ranch_discards,
            handcuffs_suit=handcuffs_suit,
        )

    def _draw_pre_checks(
        self,
        player: "Player",
        *,
        skip_heal: bool | None,
        blood_target: "Player" | None,
    ) -> bool:
        if self.event_flags.get("no_draw"):
            return True
        if self.event_flags.get("hard_liquor") and skip_heal:
            player.heal(1)
            cast(GameManagerProtocol, self).on_player_healed(player)
            return True
        custom_draw = self.event_flags.get("draw_count")
        if custom_draw is not None:
            self.draw_card(player, custom_draw)
            return True
        if self.event_flags.get("blood_brothers") and blood_target:
            self._blood_brothers_transfer(player, blood_target)
        return False

    def _dispatch_draw_listeners(
        self,
        player: "Player",
        *,
        jesse_target: "Player" | None,
        jesse_card: int | None,
        kit_back: int | None,
        pedro_use_discard: bool | None,
        jose_equipment: int | None,
        pat_target: "Player" | None,
        pat_card: str | None,
    ) -> bool:
        for cb in self.draw_phase_listeners:
            if cb(
                player,
                {
                    "jesse_target": jesse_target,
                    "jesse_card": jesse_card,
                    "kit_back": kit_back,
                    "pedro_use_discard": pedro_use_discard,
                    "jose_equipment": jose_equipment,
                    "pat_target": pat_target,
                    "pat_card": pat_card,
                },
            ):
                return True
        return False

    def _perform_draw(self, player: "Player", peyote_guesses: list[str] | None) -> None:
        if self.event_flags.get("peyote"):
            self._draw_with_peyote(player, peyote_guesses or [])
        else:
            self.draw_card(player, 2)

    def _draw_with_peyote(self, player: "Player", guesses: list[str]) -> None:
        cont = True
        while cont:
            card = self._draw_from_deck()
            if not card:
                break
            player.hand.append(card)
            guess = guesses.pop(0).lower() if guesses else "red"
            cont = self._peyote_guess_correct(card, guess)

    def _peyote_guess_correct(self, card: BaseCard, guess: str) -> bool:
        is_red = card.suit in ("Hearts", "Diamonds")
        return guess.startswith("r") and is_red or guess.startswith("b") and not is_red

    def _post_draw_events(
        self,
        player: "Player",
        *,
        ranch_discards: list[int] | None,
        handcuffs_suit: str | None,
    ) -> None:
        self._apply_law_of_the_west(player)
        if self.event_flags.get("ranch"):
            self._handle_ranch(player, ranch_discards or [])
        if self.event_flags.get("handcuffs"):
            self._set_turn_suit(handcuffs_suit)

    def _apply_law_of_the_west(self, player: "Player") -> None:
        if self.event_flags.get("law_of_the_west") and len(player.hand) >= 2:
            card = player.hand[-1]
            cast(GameManagerProtocol, self).play_card(player, card)

    def _handle_ranch(self, player: "Player", discards: list[int]) -> None:
        discards = sorted(discards, reverse=True)
        drawn = 0
        for idx in discards:
            if 0 <= idx < len(player.hand):
                discarded = player.hand.pop(idx)
                self.discard_pile.append(discarded)
                drawn += 1
        if drawn:
            self.draw_card(player, drawn)

    def _set_turn_suit(self, suit: str | None) -> None:
        self.event_flags["turn_suit"] = suit or "Hearts"

    # ------------------------------------------------------------------
    # Misc helpers
    def _blood_brothers_transfer(
        self,
        player: "Player",
        target: "Player",
    ) -> None:
        if not self.event_flags.get("blood_brothers"):
            return
        if player is target or not player.is_alive() or not target.is_alive():
            return
        if player.health <= 1:
            return
        player.take_damage(1)
        gm = cast(GameManagerProtocol, self)
        gm.on_player_damaged(player)
        target.heal(1)
        gm.on_player_healed(target)
