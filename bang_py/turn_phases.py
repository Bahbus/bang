"""Mixins for draw and discard phases."""

from __future__ import annotations

from typing import List, TYPE_CHECKING, Optional
import random

from .cards.card import BaseCard
from .characters.jesse_jones import JesseJones
from .characters.jose_delgado import JoseDelgado
from .characters.kit_carlson import KitCarlson
from .characters.pat_brennan import PatBrennan
from .characters.pedro_ramirez import PedroRamirez

if TYPE_CHECKING:
    from .game_manager import GameManager
    from .player import Player


class TurnPhasesMixin:
    """Provide draw and discard phase helpers for :class:`GameManager`."""

    deck: object
    discard_pile: List[BaseCard]
    event_flags: dict
    _players: List['Player']
    turn_order: List[int]
    current_turn: int
    phase: str
    draw_phase_listeners: List
    play_phase_listeners: List
    turn_started_listeners: List

    def _draw_from_deck(self: 'GameManager') -> BaseCard | None:
        """Draw a card reshuffling the discard pile if needed."""
        card = self.deck.draw()
        if card is None and self.discard_pile:
            self.deck.cards.extend(self.discard_pile)
            self.discard_pile.clear()
            random.shuffle(self.deck.cards)
            card = self.deck.draw()
        return card

    def draw_card(self: 'GameManager', player: 'Player', num: int = 1) -> None:
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

    def draw_phase(
        self,
        player: 'Player',
        *,
        jesse_target: 'Player' | None = None,
        jesse_card: int | None = None,
        kit_back: int | None = None,
        pedro_use_discard: bool | None = None,
        jose_equipment: int | None = None,
        pat_target: 'Player' | None = None,
        pat_card: str | None = None,
        skip_heal: bool | None = None,
        peyote_guesses: list[str] | None = None,
        ranch_discards: list[int] | None = None,
        handcuffs_suit: str | None = None,
        blood_target: 'Player' | None = None,
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
        self._post_draw_events(player, ranch_discards=ranch_discards, handcuffs_suit=handcuffs_suit)

    def _draw_pre_checks(
        self,
        player: 'Player',
        *,
        skip_heal: bool | None,
        blood_target: 'Player' | None,
    ) -> bool:
        if self.event_flags.get("no_draw"):
            return True
        if self.event_flags.get("hard_liquor") and skip_heal:
            player.heal(1)
            self.on_player_healed(player)
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
        player: 'Player',
        *,
        jesse_target: 'Player' | None,
        jesse_card: int | None,
        kit_back: int | None,
        pedro_use_discard: bool | None,
        jose_equipment: int | None,
        pat_target: 'Player' | None,
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

    def _perform_draw(self, player: 'Player', peyote_guesses: list[str] | None) -> None:
        if self.event_flags.get("peyote"):
            self._draw_with_peyote(player, peyote_guesses or [])
        else:
            self.draw_card(player, 2)

    def _draw_with_peyote(self, player: 'Player', guesses: list[str]) -> None:
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
        player: 'Player',
        *,
        ranch_discards: list[int] | None,
        handcuffs_suit: str | None,
    ) -> None:
        self._apply_law_of_the_west(player)
        if self.event_flags.get("ranch"):
            self._handle_ranch(player, ranch_discards or [])
        if self.event_flags.get("handcuffs"):
            self._set_turn_suit(handcuffs_suit)

    def _apply_law_of_the_west(self, player: 'Player') -> None:
        if self.event_flags.get("law_of_the_west") and len(player.hand) >= 2:
            card = player.hand[-1]
            self.play_card(player, card)

    def _handle_ranch(self, player: 'Player', discards: list[int]) -> None:
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

    def play_phase(self: 'GameManager', player: 'Player') -> None:
        self.phase = "play"
        for cb in self.play_phase_listeners:
            cb(player)

    def discard_phase(self: 'GameManager', player: 'Player') -> None:
        limit = self._hand_limit(player)
        self._discard_to_limit(player, limit)

    def _hand_limit(self, player: 'Player') -> int:
        limit = player.health
        if player.metadata.hand_limit is not None:
            limit = max(limit, player.metadata.hand_limit)
        if player.metadata.no_hand_limit:
            return 99
        if "reverend_limit" in self.event_flags:
            limit = min(limit, int(self.event_flags["reverend_limit"]))
        return limit

    def _discard_to_limit(self, player: 'Player', limit: int) -> None:
        while len(player.hand) > limit:
            card = player.hand.pop()
            if self.event_flags.get("abandoned_mine"):
                self.deck.cards.insert(0, card)
            else:
                self._pass_left_or_discard(player, card)

    def _blood_brothers_transfer(self: 'GameManager', player: 'Player', target: 'Player') -> None:
        if not self.event_flags.get("blood_brothers"):
            return
        if player is target or not player.is_alive() or not target.is_alive():
            return
        if player.health <= 1:
            return
        player.take_damage(1)
        self.on_player_damaged(player)
        target.heal(1)
        self.on_player_healed(target)

    # ------------------------------------------------------------------
    # Turn start helpers
    def _handle_equipment_start(self: 'GameManager', player: 'Player') -> bool:
        """Process start-of-turn equipment effects."""

        self._reactivate_green_equipment(player)
        if not self._resolve_dynamite(player):
            return False
        return self._process_jail(player)

    def _reactivate_green_equipment(self: 'GameManager', player: 'Player') -> None:
        """Refresh green equipment and reapply modifiers."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _resolve_dynamite(self: 'GameManager', player: 'Player') -> bool:
        """Handle Dynamite at turn start. Returns ``False`` if the player dies."""
        dyn = player.equipment.get("Dynamite")
        if dyn and getattr(dyn, "check_dynamite", None):
            next_idx = self.turn_order[(self.current_turn + 1) % len(self.turn_order)]
            next_player = self._players[next_idx]
            exploded = dyn.check_dynamite(player, next_player, self.deck)
            if exploded:
                self.discard_pile.append(dyn)
                self.on_player_damaged(player)
                if not player.is_alive():
                    self._begin_turn()
                    return False
        return True

    def _process_jail(self: 'GameManager', player: 'Player') -> bool:
        """Resolve Jail effects and return ``False`` if the turn is skipped."""
        jail = player.equipment.get("Jail")
        if not jail:
            return True
        if self.event_flags.get("no_jail"):
            player.unequip("Jail")
            self.discard_pile.append(jail)
            return True
        if getattr(jail, "check_turn", None):
            skipped = jail.check_turn(player, self.deck)
            self.discard_pile.append(jail)
            if skipped:
                self.current_turn = (self.current_turn + 1) % len(self.turn_order)
                self._begin_turn()
                return False
        return True

    def _handle_character_draw_abilities(self: 'GameManager', player: 'Player') -> bool:
        """Trigger characters that modify the draw phase."""

        ability_chars = (
            JesseJones,
            KitCarlson,
            PedroRamirez,
            JoseDelgado,
            PatBrennan,
        )

        if isinstance(player.character, ability_chars):
            player.metadata.awaiting_draw = True
            for cb in self.turn_started_listeners:
                cb(player)
            return True
        return False

    def _begin_turn(self: 'GameManager', *, blood_target: Optional['Player'] = None) -> None:
        if not self.turn_order:
            return
        self.current_turn %= len(self.turn_order)
        idx = self.turn_order[self.current_turn]
        player = self._players[idx]
        self.phase = "draw"
        self.reset_turn_flags(player)

        player = self._run_start_turn_checks(player)
        if not player:
            return

        self.draw_phase(player, blood_target=blood_target)
        self.play_phase(player)
        player.metadata.bangs_played = 0
        for cb in self.turn_started_listeners:
            cb(player)

    def _run_start_turn_checks(self: 'GameManager', player: 'Player') -> Optional['Player']:
        """Apply start-of-turn effects returning the acting player or ``None``."""
        player = self._apply_event_start_effects(player)
        if not player:
            return None
        if self._maybe_revive_ghost_town(player):
            return None
        if not self._handle_equipment_start(player):
            return None
        if self._handle_character_draw_abilities(player):
            return None
        return player

    def end_turn(self: 'GameManager') -> None:
        """Finish the current player's turn and advance to the next."""
        if not self.turn_order:
            return
        idx = self.turn_order[self.current_turn]
        player = self._players[idx]
        self.phase = "discard"
        self.discard_phase(player)
        self.event_flags.pop("turn_suit", None)
        self._reset_green_equipment(player)
        if self._handle_vendetta(player):
            return
        self._finish_ghost_town(player)
        self._advance_turn()

    # ------------------------------------------------------------------
    # Turn end helpers
    def _reset_green_equipment(self: 'GameManager', player: 'Player') -> None:
        """Reactivate green equipment at the end of the turn."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _advance_turn(self: 'GameManager') -> None:
        """Move the turn pointer and start the next turn."""
        if self.event_flags.get("reverse_turn"):
            self.current_turn = (self.current_turn - 1) % len(self.turn_order)
        else:
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        self._begin_turn()

