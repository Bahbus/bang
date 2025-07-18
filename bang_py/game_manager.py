"""Manage overall game state and turn progression for Bang."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import random

from .deck import Deck
from .deck_factory import create_standard_deck
from .cards.card import BaseCard
from .helpers import handle_out_of_turn_discard
from .characters.jesse_jones import JesseJones
from .characters.jose_delgado import JoseDelgado
from .characters.kit_carlson import KitCarlson
from .characters.pat_brennan import PatBrennan
from .characters.pedro_ramirez import PedroRamirez
from .characters.vera_custer import VeraCuster
from .cards.bang import BangCard
from .cards.missed import MissedCard
from .cards.stagecoach import StagecoachCard
from .cards.wells_fargo import WellsFargoCard
from .cards.cat_balou import CatBalouCard
from .cards.panic import PanicCard
from .cards.jail import JailCard
from .cards.indians import IndiansCard
from .cards.duel import DuelCard
from .cards.general_store import GeneralStoreCard
from .cards.saloon import SaloonCard
from .cards.gatling import GatlingCard
from .cards.howitzer import HowitzerCard
from .cards.punch import PunchCard
from .cards.knife import KnifeCard
from .cards.brawl import BrawlCard
from .cards.springfield import SpringfieldCard
from .cards.whisky import WhiskyCard
from .cards.beer import BeerCard
from .cards.high_noon_card import HighNoonCard
from .cards.pony_express import PonyExpressCard
from .cards.tequila import TequilaCard
from .cards.rag_time import RagTimeCard
from .cards.bible import BibleCard
from .cards.canteen import CanteenCard
from .cards.conestoga import ConestogaCard
from .cards.can_can import CanCanCard
from .cards.buffalo_rifle import BuffaloRifleCard
from .cards.pepperbox import PepperboxCard
from .cards.derringer import DerringerCard

from .player import Player
from .cards.roles import (
    BaseRole,
    DeputyRoleCard,
    OutlawRoleCard,
    RenegadeRoleCard,
    SheriffRoleCard,
)
from .characters.base import BaseCharacter
from .event_decks import (
    EventCard,
    create_high_noon_deck,
    create_fistful_deck,
)


@dataclass
class GameManager:
    """Manage players, deck and discard pile.

    Controls turn order and triggers game events.
    """

    players: List[Player] = field(default_factory=list)
    deck: Deck | None = None
    expansions: List[str] = field(default_factory=list)
    discard_pile: List[BaseCard] = field(default_factory=list)
    current_turn: int = 0
    turn_order: List[int] = field(default_factory=list)
    event_deck: List[EventCard] | None = None
    current_event: EventCard | None = None
    event_flags: dict = field(default_factory=dict)
    first_eliminated: Player | None = None
    sheriff_turns: int = 0
    phase: str = "draw"

    # General Store state
    general_store_cards: List[BaseCard] | None = None
    general_store_order: List[Player] | None = None
    general_store_index: int = 0

    # Event listeners
    draw_phase_listeners: List[Callable[[Player, object], bool]] = field(
        default_factory=list
    )
    player_damaged_listeners: List[Callable[[Player, Player | None], None]] = field(
        default_factory=list
    )
    player_healed_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    player_death_listeners: List[Callable[[Player, Player | None], None]] = field(
        default_factory=list
    )
    turn_started_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    game_over_listeners: List[Callable[[str], None]] = field(default_factory=list)
    card_play_checks: List[
        Callable[[Player, BaseCard, Optional[Player]], bool]
    ] = field(default_factory=list)
    card_played_listeners: List[
        Callable[[Player, BaseCard, Optional[Player]], None]
    ] = field(default_factory=list)
    play_phase_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    _duel_counts: dict | None = field(default=None, init=False, repr=False)

    def prompt_new_identity(self, player: Player) -> bool:
        """Return True if the player opts to switch characters."""
        return True

    def draw_event_card(self) -> None:
        """Draw and apply the next event card."""
        if not self.event_deck:
            return
        self.current_event = self.event_deck.pop(0)
        self.event_flags.clear()
        self.current_event.apply(self)

    def __post_init__(self) -> None:
        """Initialize decks and register card handlers."""
        self._initialize_main_deck()
        self._initialize_event_deck()
        self._register_card_handlers()

    # ------------------------------------------------------------------
    # Initialization helpers
    def _initialize_main_deck(self) -> None:
        """Create the main deck if needed and ensure event flags exist."""
        if self.deck is None:
            if not self.expansions:
                self.expansions.append("dodge_city")
            self.deck = create_standard_deck(self.expansions)
        self.event_flags = {}

    def _initialize_event_deck(self) -> None:
        """Build and shuffle the event deck based on active expansions."""
        if "high_noon" in self.expansions:
            self.event_deck = self._prepare_high_noon_deck()
        elif "fistful_of_cards" in self.expansions:
            self.event_deck = self._prepare_fistful_deck()
        elif self.event_deck:
            random.shuffle(self.event_deck)

    def _prepare_high_noon_deck(self) -> List[EventCard] | None:
        """Create and shuffle the High Noon event deck."""
        deck = create_high_noon_deck()
        if deck:
            final = next((c for c in deck if c.name == "High Noon"), None)
            if final:
                deck.remove(final)
                random.shuffle(deck)
                deck.append(final)
        return deck

    def _prepare_fistful_deck(self) -> List[EventCard] | None:
        """Create and shuffle the Fistful of Cards event deck."""
        deck = create_fistful_deck()
        if deck:
            final = next((c for c in deck if c.name == "A Fistful of Cards"), None)
            if final:
                deck.remove(final)
                random.shuffle(deck)
                deck.append(final)
        return deck

    def add_player(self, player: Player) -> None:
        """Add a player to the game and record the game reference."""
        player.metadata.game = self
        self.players.append(player)
        if player.character is not None:
            player.character.ability(self, player)

    def remove_player(self, player: Player) -> None:
        """Remove ``player`` from the game and update turn order."""
        if player not in self.players:
            return

        current_obj = self._current_player_obj() if self.turn_order else None

        idx = self.players.index(player)
        self.players.pop(idx)
        player.metadata.game = None
        self._reindex_turn_order(idx)
        if not self.turn_order:
            self.current_turn = 0
            return

        self._reset_current_turn(current_obj)


    def start_game(self, deal_roles: bool = True) -> None:
        """Begin the game and deal starting hands."""

        if deal_roles:
            self._deal_roles_and_characters()
        self.turn_order = list(range(len(self.players)))
        self.current_turn = 0
        # Deal initial hands
        for _ in range(2):
            for player in self.players:
                self.draw_card(player)
        self._begin_turn()

    # ------------------------------------------------------------------
    # Setup helpers
    def _build_role_deck(self) -> List[BaseRole]:
        role_map = {
            3: [DeputyRoleCard, OutlawRoleCard, RenegadeRoleCard],
            4: [SheriffRoleCard, RenegadeRoleCard, OutlawRoleCard, OutlawRoleCard],
            5: [
                SheriffRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
            6: [
                SheriffRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
            7: [
                SheriffRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
            8: [
                SheriffRoleCard,
                RenegadeRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
        }
        classes = role_map.get(len(self.players))
        if not classes:
            raise ValueError("Unsupported player count")
        return [cls() for cls in classes]

    def _build_character_deck(self) -> List[type[BaseCharacter]]:
        from . import characters

        return [
            getattr(characters, name)
            for name in characters.__all__
            if name != "BaseCharacter"
        ]

    def choose_character(
        self, player: Player, options: List[BaseCharacter]
    ) -> BaseCharacter:
        """Select which character a player will use. Defaults to the first."""
        return options[0]

    def apply_new_identity(self, player: Player) -> None:
        """Swap ``player`` to their unused character if the new identity event is active."""

        if not self.event_flags.get("new_identity"):
            return
        new_char = player.metadata.unused_character
        if not new_char:
            return
        old_char = player.character
        player.character = new_char
        player.metadata.unused_character = old_char
        player.reset_stats()
        player.character.ability(self, player)
        player.health = min(2, player.max_health)

    def _deal_roles_and_characters(self) -> None:
        role_deck = self._build_role_deck()
        random.shuffle(role_deck)
        char_deck = [cls() for cls in self._build_character_deck()]
        random.shuffle(char_deck)

        for player in self.players:
            player.role = role_deck.pop()
            choices = [char_deck.pop(), char_deck.pop()]
            chosen = self.choose_character(player, choices)
            player.character = chosen
            for ch in choices:
                if ch is not chosen:
                    player.metadata.unused_character = ch
                    break
            player.reset_stats()
            player.character.ability(self, player)
            player.metadata.game = self

    def _apply_event_start_effects(self, player: Player) -> Player | None:
        """Run start-of-turn event logic.

        Return the acting player or ``None`` if they are eliminated or skipped.
        """
        pre_ghost = self.event_flags.get("ghost_town")
        player = self._sheriff_event_updates(player, bool(pre_ghost))

        self._process_new_identity(player)

        if self._skip_turn_if_needed():
            return None

        if not self._apply_start_damage(player):
            return None

        if not self._apply_fistful_of_cards(player):
            return None

        self._handle_dead_man(player)

        return player

    def _sheriff_event_updates(self, player: Player, pre_ghost: bool) -> Player:
        """Update sheriff-related counters and Ghost Town clean up."""
        if isinstance(player.role, SheriffRoleCard):
            self._increment_sheriff_turns()
            if pre_ghost and self.event_deck and self.sheriff_turns >= 2:
                player = self._ghost_town_cleanup(player)
        return player

    # ------------------------------------------------------------------
    # Sheriff helpers
    def _increment_sheriff_turns(self) -> None:
        """Increment sheriff turn count and draw events when eligible."""
        self.sheriff_turns += 1
        if self.event_deck and self.sheriff_turns >= 2:
            self.draw_event_card()

    def _ghost_town_cleanup(self, player: Player) -> Player:
        """Remove revived ghosts once the sheriff has taken two turns."""
        removed = False
        for pl in self.players:
            if pl.metadata.ghost_revived and pl.is_alive():
                pl.health = 0
                pl.metadata.ghost_revived = False
                removed = True
        if removed:
            self.turn_order = [i for i, pl in enumerate(self.players) if pl.is_alive()]
            self.current_turn = self.turn_order.index(self.players.index(player))
            idx = self.turn_order[self.current_turn]
            player = self.players[idx]
        return player

    def _process_new_identity(self, player: Player) -> None:
        """Handle the New Identity event for ``player``."""
        if self.event_flags.get("new_identity") and player.metadata.unused_character:
            if self.prompt_new_identity(player):
                self.apply_new_identity(player)

    def _skip_turn_if_needed(self) -> bool:
        """Skip the current turn if the corresponding event is active."""
        if self.event_flags.get("skip_turn"):
            self.event_flags.pop("skip_turn")
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
            self._begin_turn()
            return True
        return False

    def _apply_start_damage(self, player: Player) -> bool:
        """Apply start-of-turn damage to ``player`` if required."""
        dmg = self.event_flags.get("start_damage", 0)
        if dmg:
            player.take_damage(dmg)
            self.on_player_damaged(player)
            if not player.is_alive():
                self._begin_turn()
                return False
        return True

    def _apply_fistful_of_cards(self, player: Player) -> bool:
        """Resolve the Fistful of Cards effect against ``player``."""
        if self.event_flags.get("fistful_of_cards"):
            for _ in range(len(player.hand)):
                if not self._auto_miss(player):
                    player.take_damage(1)
                    self.on_player_damaged(player)
                    if not player.is_alive():
                        self._begin_turn()
                        return False
        return True

    def _handle_dead_man(self, player: Player) -> None:
        """Apply the Dead Man event to ``player`` if applicable."""
        if (
            self.event_flags.get("dead_man")
            and self.event_flags.get("dead_man_player") is player
            and not player.is_alive()
            and not self.event_flags.get("dead_man_used")
        ):
            player.health = 2
            self.draw_card(player, 2)
            self.event_flags["dead_man_used"] = True

    def _maybe_revive_ghost_town(self, player: Player) -> bool:
        """Revive ``player`` if Ghost Town is active.

        Return ``True`` if revived so no further start actions occur.
        """
        if self.event_flags.get("ghost_town") and not player.is_alive():
            player.health = 1
            player.metadata.ghost_revived = True
            self.draw_card(player, 3)
            player.metadata.bangs_played = 0
            for cb in self.turn_started_listeners:
                cb(player)
            return True
        return False

    def _handle_equipment_start(self, player: Player) -> bool:
        """Process start-of-turn equipment effects.

        Reactivates green equipment, resolves Dynamite and Jail, and returns
        ``True`` if the player's turn should continue.
        """
        self._reactivate_green_equipment(player)
        if not self._resolve_dynamite(player):
            return False
        return self._process_jail(player)

    # ------------------------------------------------------------------
    # Equipment helpers
    def _reactivate_green_equipment(self, player: Player) -> None:
        """Refresh green equipment and reapply modifiers."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _resolve_dynamite(self, player: Player) -> bool:
        """Handle Dynamite at turn start. Returns ``False`` if the player dies."""
        dyn = player.equipment.get("Dynamite")
        if dyn and getattr(dyn, "check_dynamite", None):
            next_idx = self.turn_order[(self.current_turn + 1) % len(self.turn_order)]
            next_player = self.players[next_idx]
            exploded = dyn.check_dynamite(player, next_player, self.deck)
            if exploded:
                self.discard_pile.append(dyn)
                self.on_player_damaged(player)
                if not player.is_alive():
                    self._begin_turn()
                    return False
        return True

    def _process_jail(self, player: Player) -> bool:
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

    def _handle_character_draw_abilities(self, player: Player) -> bool:
        """Trigger characters that modify the draw phase.

        Returns ``True`` if the standard draw and play phases should be skipped.
        """
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

    def _begin_turn(self, *, blood_target: Player | None = None) -> None:
        if not self.turn_order:
            return
        self.current_turn %= len(self.turn_order)
        idx = self.turn_order[self.current_turn]
        player = self.players[idx]
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

    def _run_start_turn_checks(self, player: Player) -> Player | None:
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

    def end_turn(self) -> None:
        if not self.turn_order:
            return
        idx = self.turn_order[self.current_turn]
        player = self.players[idx]
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
    def _reset_green_equipment(self, player: Player) -> None:
        """Reactivate green equipment at the end of the turn."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _handle_vendetta(self, player: Player) -> bool:
        """Resolve the Vendetta event. Return ``True`` if an extra turn occurs."""
        if (
            not self.event_flags.get("vendetta")
            or player in self.event_flags.get("vendetta_used", set())
        ):
            return False
        card = self._draw_from_deck()
        if card:
            self.discard_pile.append(card)
            if card.suit == "Hearts":
                self.event_flags.setdefault("vendetta_used", set()).add(player)
                self._begin_turn()
                return True
        return False

    def _finish_ghost_town(self, player: Player) -> None:
        """Remove temporary Ghost Town revival at turn end."""
        if self.event_flags.get("ghost_town") and player.metadata.ghost_revived:
            player.health = 0
            player.metadata.ghost_revived = False
            self._check_win_conditions()

    def _advance_turn(self) -> None:
        """Move the turn pointer and start the next turn."""
        if self.event_flags.get("reverse_turn"):
            self.current_turn = (self.current_turn - 1) % len(self.turn_order)
        else:
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        self._begin_turn()

    def _draw_from_deck(self) -> BaseCard | None:
        """Draw a card reshuffling the discard pile if the deck is empty."""
        card = self.deck.draw()
        if card is None and self.discard_pile:
            self.deck.cards.extend(self.discard_pile)
            self.discard_pile.clear()
            random.shuffle(self.deck.cards)
            card = self.deck.draw()
        return card

    def draw_card(self, player: Player, num: int = 1) -> None:
        """Draw ``num`` cards for ``player`` applying active event effects."""

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
        player: Player,
        *,
        jesse_target: Player | None = None,
        jesse_card: int | None = None,
        kit_back: int | None = None,
        pedro_use_discard: bool | None = None,
        jose_equipment: int | None = None,
        pat_target: Player | None = None,
        pat_card: str | None = None,

        skip_heal: bool | None = None,
        peyote_guesses: list[str] | None = None,
        ranch_discards: list[int] | None = None,
        handcuffs_suit: str | None = None,
        blood_target: Player | None = None,

    ) -> None:
        """Run the draw phase for ``player`` with optional selections."""

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
        player: Player,
        *,
        skip_heal: bool | None,
        blood_target: Player | None,
    ) -> bool:
        """Handle early draw-phase events. Returns ``True`` if phase ends."""
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
        player: Player,
        *,
        jesse_target: Player | None,
        jesse_card: int | None,
        kit_back: int | None,
        pedro_use_discard: bool | None,
        jose_equipment: int | None,
        pat_target: Player | None,
        pat_card: str | None,
    ) -> bool:
        """Notify draw phase listeners, returning ``True`` to stop."""
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

    def _perform_draw(
        self, player: Player, peyote_guesses: list[str] | None
    ) -> None:
        """Execute the actual card draws for the phase."""
        if self.event_flags.get("peyote"):
            self._draw_with_peyote(player, peyote_guesses or [])
        else:
            self.draw_card(player, 2)

    def _draw_with_peyote(self, player: Player, guesses: list[str]) -> None:
        """Handle the Peyote event drawing loop."""
        cont = True
        while cont:
            card = self._draw_from_deck()
            if not card:
                break
            player.hand.append(card)
            guess = guesses.pop(0).lower() if guesses else "red"
            cont = self._peyote_guess_correct(card, guess)

    def _peyote_guess_correct(self, card: BaseCard, guess: str) -> bool:
        """Return ``True`` if the peyote guess was correct."""
        is_red = card.suit in ("Hearts", "Diamonds")
        return guess.startswith("r") and is_red or guess.startswith("b") and not is_red

    def _post_draw_events(
        self,
        player: Player,
        *,
        ranch_discards: list[int] | None,
        handcuffs_suit: str | None,
    ) -> None:
        """Handle effects that trigger after cards are drawn."""
        self._apply_law_of_the_west(player)
        if self.event_flags.get("ranch"):
            self._handle_ranch(player, ranch_discards or [])
        if self.event_flags.get("handcuffs"):
            self._set_turn_suit(handcuffs_suit)

    def _apply_law_of_the_west(self, player: Player) -> None:
        """Immediately play the last drawn card if Law of the West is active."""
        if self.event_flags.get("law_of_the_west") and len(player.hand) >= 2:
            card = player.hand[-1]
            self.play_card(player, card)

    def _handle_ranch(self, player: Player, discards: list[int]) -> None:
        """Discard selected cards and redraw when The Ranch is active."""
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
        """Record the suit restriction for the Handcuffs event."""
        self.event_flags["turn_suit"] = suit or "Hearts"

    def play_phase(self, player: Player) -> None:
        """Signal the start of the play phase for ``player``."""
        self.phase = "play"
        for cb in self.play_phase_listeners:
            cb(player)

    def discard_phase(self, player: Player) -> None:
        """Discard down to the player's hand limit at the end of their turn."""
        limit = player.health
        if player.metadata.hand_limit is not None:
            limit = max(limit, player.metadata.hand_limit)
        if player.metadata.no_hand_limit:
            limit = 99
        if "reverend_limit" in self.event_flags:
            limit = min(limit, int(self.event_flags["reverend_limit"]))
        while len(player.hand) > limit:
            card = player.hand.pop()
            if self.event_flags.get("abandoned_mine"):
                self.deck.cards.insert(0, card)
            else:
                self._pass_left_or_discard(player, card)

    def _pre_card_checks(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> bool:
        return (
            self._card_in_hand(player, card)
            and self._run_card_play_checks(player, card, target)
            and self._check_target_restrictions(player, card, target)
            and self._check_event_restrictions(player, card)
        )

    def _card_in_hand(self, player: Player, card: BaseCard) -> bool:
        """Return ``True`` if ``card`` is currently in ``player``'s hand."""
        return card in player.hand

    def _run_card_play_checks(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> bool:
        """Execute registered pre-play checks."""
        for cb in self.card_play_checks:
            if not cb(player, card, target):
                return False
        return True

    def _check_target_restrictions(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> bool:
        """Validate distance and target based limitations."""
        return (
            self._bang_target_valid(player, card, target)
            and self._panic_target_valid(player, card, target)
            and self._jail_target_valid(card, target)
        )

    # ------------------------------------------------------------------
    # Target restriction helpers
    def _bang_target_valid(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> bool:
        """Check range and sniper restrictions for Bang! cards."""
        if not (isinstance(card, BangCard) and target):
            return True
        if player.distance_to(target) > player.attack_range:
            return False
        if self.event_flags.get("sniper") and player.metadata.use_sniper:
            bang_count = sum(isinstance(c, BangCard) for c in player.hand)
            return bang_count >= 2
        return True

    def _panic_target_valid(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> bool:
        """Panic can only target players within distance 1."""
        if isinstance(card, PanicCard) and target:
            return player.distance_to(target) <= 1
        return True

    def _jail_target_valid(self, card: BaseCard, target: Optional[Player]) -> bool:
        """Jail cannot be played on the sheriff."""
        if isinstance(card, JailCard) and target and isinstance(target.role, SheriffRoleCard):
            return False
        return True

    def _check_event_restrictions(
        self, player: Player, card: BaseCard
    ) -> bool:
        """Check event related card play restrictions."""
        return not (
            self._jail_blocked(card)
            or self._judge_blocked(card)
            or self._handcuffs_blocked(player, card)
        )

    def _jail_blocked(self, card: BaseCard) -> bool:
        """Return ``True`` if Jail cards are currently banned."""
        return self.event_flags.get("no_jail") and isinstance(card, JailCard)

    def _judge_blocked(self, card: BaseCard) -> bool:
        """Return ``True`` if equipment cards are disallowed by The Judge."""
        return self.event_flags.get("judge") and card.card_type in {"equipment", "green"}

    def _handcuffs_blocked(self, player: Player, card: BaseCard) -> bool:
        """Return ``True`` if Handcuffs restricts ``player`` from playing ``card``."""
        if not self.event_flags.get("handcuffs") or not self.event_flags.get("turn_suit"):
            return False
        active = self.players[self.turn_order[self.current_turn]]
        return player is active and getattr(card, "suit", None) != self.event_flags["turn_suit"]

    def _is_bang(self, player: Player, card: BaseCard, target: Optional[Player]) -> bool:
        return isinstance(card, BangCard) or (
            player.metadata.play_missed_as_bang and isinstance(card, MissedCard) and target
        )

    def _can_play_bang(self, player: Player) -> bool:
        if self.event_flags.get("no_bang"):
            return False
        count = player.metadata.bangs_played
        gun = player.equipment.get("Gun")
        extra = player.metadata.doc_free_bang
        unlimited = (
            player.metadata.unlimited_bang
            or getattr(gun, "unlimited_bang", False)
            or extra > 0
        )
        limit = self.event_flags.get("bang_limit", 1)
        return count < limit or unlimited

    def _dispatch_play(self, player: Player, card: BaseCard, target: Optional[Player]) -> None:
        if self._handle_missed_as_bang(player, card, target):
            return
        handler = self._card_handlers.get(type(card))
        if handler:
            handler(player, card, target)
        else:
            card.play(target)

    def _handle_missed_as_bang(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> bool:
        """Treat a Missed! card as Bang! when allowed."""
        if player.metadata.play_missed_as_bang and isinstance(card, MissedCard) and target:
            handler = self._card_handlers.get(BangCard)
            if handler:
                handler(player, BangCard(), target)
            return True
        return False

    def _play_bang_card(self, player: Player, card: BangCard, target: Optional[Player]) -> None:
        ignore_eq = player.metadata.ignore_others_equipment
        extra_bang = self._consume_sniper_extra(player, card)
        need_two = player.metadata.double_miss or extra_bang
        if target and need_two:
            if not self._attempt_double_dodge(target):
                card.play(target, self.deck, ignore_equipment=ignore_eq)
        else:
            if not (target and self._auto_miss(target)):
                card.play(target, self.deck, ignore_equipment=ignore_eq)

    def _consume_sniper_extra(self, player: Player, card: BangCard) -> bool:
        """Handle Sniper event extra Bang! consumption."""
        if self.event_flags.get("sniper") and player.metadata.use_sniper:
            extra = next(
                (c for c in player.hand if isinstance(c, BangCard) and c is not card),
                None,
            )
            player.metadata.use_sniper = False
            if extra:
                player.hand.remove(extra)
                self._pass_left_or_discard(player, extra)
                return True
        return False

    def _attempt_double_dodge(self, target: Player) -> bool:
        """Let ``target`` discard two Missed! cards to avoid damage."""
        misses = [c for c in target.hand if isinstance(c, MissedCard)]
        if len(misses) >= 2:
            for _ in range(2):
                mcard = misses.pop()
                target.hand.remove(mcard)
                self.discard_pile.append(mcard)
                handle_out_of_turn_discard(self, target, mcard)
            target.metadata.dodged = True
            return True
        return False

    def _handler_self_game(self, player: Player, card: BaseCard, target: Optional[Player]) -> None:
        """Play the card on the acting player with game context."""
        card.play(player, game=self)

    def _handler_target_game(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> None:
        """Play the card on ``target`` if provided using the game context."""
        if target:
            card.play(target, game=self)

    def _handler_target_player_game(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> None:
        """Play the card on ``target`` with ``player`` and game context."""
        if target:
            card.play(target, player, game=self)

    def _handler_self_player_game(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> None:
        """Play the card on the acting player with themselves as the target."""
        card.play(player, player, game=self)

    def _handler_target_or_self_player_game(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> None:
        """Play on ``target`` if provided otherwise on ``player`` with game context."""
        card.play(target or player, player, game=self)

    def _handler_target_player(
        self, player: Player, card: BaseCard, target: Optional[Player]
    ) -> None:
        """Play on ``target`` with ``player`` as context but without game."""
        if target:
            card.play(target, player)

    def _register_card_handlers(self) -> None:
        self._card_handlers = {
            BangCard: self._play_bang_card,
            StagecoachCard: self._handler_self_game,
            WellsFargoCard: self._handler_self_game,
            CatBalouCard: self._handler_target_game,
            PanicCard: self._handler_target_player_game,
            IndiansCard: self._handler_self_player_game,
            DuelCard: self._handler_target_player_game,
            GeneralStoreCard: self._handler_self_player_game,
            SaloonCard: self._handler_self_player_game,
            GatlingCard: self._handler_self_player_game,
            HowitzerCard: self._handler_self_player_game,
            WhiskyCard: self._handler_target_or_self_player_game,
            BeerCard: self._handler_target_or_self_player_game,
            PonyExpressCard: self._handler_self_player_game,
            TequilaCard: self._handler_target_or_self_player_game,
            HighNoonCard: self._handler_self_player_game,
            PunchCard: self._handler_target_player,
            KnifeCard: self._handler_target_player_game,
            BrawlCard: self._handler_self_player_game,
            SpringfieldCard: self._handler_target_player_game,
            RagTimeCard: self._handler_target_player_game,
            BibleCard: self._handler_target_or_self_player_game,
            CanteenCard: self._handler_target_or_self_player_game,
            ConestogaCard: self._handler_target_player_game,
            CanCanCard: self._handler_target_game,
            BuffaloRifleCard: self._handler_target_player_game,
            PepperboxCard: self._handler_target_player_game,
            DerringerCard: self._handler_target_player_game,
        }

    def play_card(self, player: Player, card: BaseCard, target: Optional[Player] = None) -> None:
        if not self._pre_card_checks(player, card, target):
            return

        is_bang = self._is_bang(player, card, target)
        if is_bang and not self._can_play_bang(player):
            return

        player.hand.remove(card)
        before = target.health if target else None
        self._dispatch_play(player, card, target)
        self._notify_card_played(player, card, target)
        self._apply_post_play(player, card, target, before, is_bang)

    def _notify_card_played(self, player: Player, card: BaseCard, target: Optional[Player]) -> None:
        """Call registered card played listeners."""
        for cb in self.card_played_listeners:
            cb(player, card, target)

    def _apply_post_play(
        self,
        player: Player,
        card: BaseCard,
        target: Optional[Player],
        before: Optional[int],
        is_bang: bool,
    ) -> None:
        """Handle damage, discard and Bang! bookkeeping."""
        self._apply_damage_and_healing(player, target, before)
        self._pass_left_or_discard(player, card)
        if is_bang:
            self._update_bang_counters(player)
        self._draw_if_empty(player)

    def _apply_damage_and_healing(
        self, source: Player, target: Optional[Player], before: Optional[int]
    ) -> None:
        """Trigger damage or heal callbacks if ``target`` changed health."""
        if target and before is not None:
            if target.health < before:
                self.on_player_damaged(target, source)
            elif target.health > before:
                self.on_player_healed(target)

    def _draw_if_empty(self, player: Player) -> None:
        """Draw a card if the player has an empty hand and may draw."""
        if player.metadata.draw_when_empty and not player.hand:
            self.draw_card(player)

    def _update_bang_counters(self, player: Player) -> None:
        """Update Bang! play counters for ``player``."""
        if player.metadata.doc_free_bang > 0:
            player.metadata.doc_free_bang -= 1
        else:
            player.metadata.bangs_played += 1

    def discard_card(self, player: Player, card: BaseCard) -> None:
        if card in player.hand:
            player.hand.remove(card)
            self._pass_left_or_discard(player, card)
            if not self.event_flags.get("river"):
                handle_out_of_turn_discard(self, player, card)
            if player.metadata.draw_when_empty and not player.hand:
                self.draw_card(player)

    def sid_ketchum_ability(self, player: Player, indices: List[int] | None = None) -> None:
        if len(player.hand) < 2 or player.health >= player.max_health:
            return
        discard_indices = indices or list(range(2))
        discard_indices = sorted(discard_indices, reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                self._pass_left_or_discard(player, card)
        player.heal(1)
        self.on_player_healed(player)

    def _auto_miss(self, target: Player) -> bool:
        if not self._should_use_auto_miss(target):
            return False
        if self._use_miss_card(target):
            return True
        if self._use_bang_as_miss(target):
            return True
        if self._use_any_card_as_miss(target):
            return True
        return False

    def _should_use_auto_miss(self, target: Player) -> bool:
        """Return ``True`` if automatic Missed! can be used."""
        if self.event_flags.get("no_missed"):
            return False
        return target.metadata.auto_miss is not False

    def _discard_and_record(self, player: Player, card: BaseCard) -> None:
        self._pass_left_or_discard(player, card)
        if not self.event_flags.get("river"):
            handle_out_of_turn_discard(self, player, card)

    def _use_miss_card(self, target: Player) -> bool:
        miss = next((c for c in target.hand if isinstance(c, MissedCard)), None)
        if miss:
            target.hand.remove(miss)
            self._discard_and_record(target, miss)
            target.metadata.dodged = True
            return True
        return False

    def _use_bang_as_miss(self, target: Player) -> bool:
        if target.metadata.bang_as_missed:
            bang = next((c for c in target.hand if isinstance(c, BangCard)), None)
            if bang:
                target.hand.remove(bang)
                self._discard_and_record(target, bang)
                target.metadata.dodged = True
                return True
        return False

    def _use_any_card_as_miss(self, target: Player) -> bool:
        if target.metadata.any_card_as_missed and target.hand:
            card = target.hand.pop()
            self._discard_and_record(target, card)
            target.metadata.dodged = True
            return True
        return False

    def chuck_wengam_ability(self, player: Player) -> None:
        """Lose 1 life to draw 2 cards, usable multiple times per turn."""
        if player.health <= 1:
            return
        player.take_damage(1)
        self.on_player_damaged(player)
        self.draw_card(player, 2)

    def doc_holyday_ability(self, player: Player, indices: List[int] | None = None) -> None:
        """Discard two cards to gain a Bang! that doesn't count toward the limit."""
        if player.metadata.doc_used:
            return
        if len(player.hand) < 2:
            return
        discard_indices = indices or list(range(2))
        discard_indices = sorted(discard_indices, reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                self._pass_left_or_discard(player, card)
        player.metadata.doc_used = True
        player.metadata.doc_free_bang += 1
        player.hand.append(BangCard())

    def pat_brennan_draw(
        self,
        player: Player,
        target: Player | None = None,
        card_name: str | None = None,
    ) -> bool:
        """During draw phase, draw a card in play instead of from deck."""
        targets = [t for t in self.players if t is not player]
        if target in targets and card_name and card_name in target.equipment:
            card = target.unequip(card_name)
            if card:
                player.hand.append(card)
                return True
        for p in targets:
            for card in list(p.equipment.values()):
                p.unequip(card.card_name)
                player.hand.append(card)
                return True
        return False

    def uncle_will_ability(self, player: Player, card: BaseCard) -> bool:
        """Play any card as General Store once per turn."""
        if player.metadata.uncle_used:
            return False
        player.metadata.uncle_used = True
        GeneralStoreCard().play(player, player, game=self)
        player.hand.remove(card)
        self._pass_left_or_discard(player, card)
        return True

    def vera_custer_copy(self, player: Player, target: Player) -> None:
        """Copy another living character's ability for the turn."""
        if not isinstance(player.character, VeraCuster):
            return
        if not target.is_alive() or target is player:
            return
        player.metadata.vera_copy = target.character.__class__
        player.metadata.abilities.add(target.character.__class__)
        target.character.ability(self, player)

    def _blood_brothers_transfer(self, player: Player, target: Player) -> None:
        """Transfer one health from ``player`` to ``target`` if possible."""
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

    def ricochet_shoot(self, player: Player, target: Player, card_name: str) -> bool:
        """Discard a Bang! to shoot at ``card_name`` in front of ``target``."""
        if not self.event_flags.get("ricochet"):
            return False
        bang = next((c for c in player.hand if isinstance(c, BangCard)), None)
        card = target.equipment.get(card_name)
        if not bang or not card:
            return False
        player.hand.remove(bang)
        self._pass_left_or_discard(player, bang)
        miss = next((c for c in target.hand if isinstance(c, MissedCard)), None)
        if miss:
            target.hand.remove(miss)
            self._pass_left_or_discard(target, miss)
            handle_out_of_turn_discard(self, target, miss)
            return False
        target.unequip(card_name)
        self.discard_pile.append(card)
        return True

    # General Store management
    def start_general_store(self, player: Player) -> List[str]:
        """Draw cards for General Store and record selection order."""
        if not self.deck:
            return []
        self.general_store_cards = self._deal_general_store_cards()
        self._set_general_store_order(player)
        return [c.card_name for c in self.general_store_cards]

    def _deal_general_store_cards(self) -> List[BaseCard]:
        """Draw one card per living player for General Store."""
        alive = [p for p in self.players if p.is_alive()]
        cards: List[BaseCard] = []
        for _ in range(len(alive)):
            card = self._draw_from_deck()
            if card:
                cards.append(card)
        return cards

    def _set_general_store_order(self, player: Player) -> None:
        """Determine the order of selection for General Store."""
        start_idx = self.players.index(player)
        order: List[Player] = []
        for i in range(len(self.players)):
            p = self.players[(start_idx + i) % len(self.players)]
            if p.is_alive():
                order.append(p)
        self.general_store_order = order
        self.general_store_index = 0

    def general_store_pick(self, player: Player, index: int) -> bool:
        """Give the chosen card to the current player."""
        if not self._valid_general_store_pick(player, index):
            return False
        card = self.general_store_cards.pop(index)
        player.hand.append(card)
        self.general_store_index += 1
        if self.general_store_index >= len(self.general_store_order):
            self._cleanup_general_store_leftovers()
        return True

    def _valid_general_store_pick(self, player: Player, index: int) -> bool:
        """Return ``True`` if ``player`` may pick ``index``."""
        if (
            self.general_store_cards is None
            or self.general_store_order is None
            or self.general_store_index >= len(self.general_store_order)
            or self.general_store_order[self.general_store_index] is not player
        ):
            return False
        return 0 <= index < len(self.general_store_cards)

    def _cleanup_general_store_leftovers(self) -> None:
        """Discard any unclaimed General Store cards."""
        for leftover in self.general_store_cards:
            self.discard_pile.append(leftover)
        self.general_store_cards = None
        self.general_store_order = None
        self.general_store_index = 0

    def reset_turn_flags(self, player: Player) -> None:
        player.metadata.doc_used = False
        player.metadata.doc_free_bang = 0
        player.metadata.uncle_used = False
        if isinstance(player.character, VeraCuster):
            player.metadata.vera_copy = None
            player.metadata.unlimited_bang = False
            player.metadata.ignore_others_equipment = False
            player.metadata.no_hand_limit = False
            player.metadata.double_miss = False
            player.metadata.draw_when_empty = False
            player.metadata.immune_diamond = False
            player.metadata.play_missed_as_bang = False
            player.metadata.bang_as_missed = False
            player.metadata.any_card_as_missed = False
            player.metadata.lucky_duke = False
            player.metadata.virtual_barrel = False
            player.metadata.beer_heal_bonus = 0
            player.metadata.hand_limit = None
            player.metadata.abilities = {VeraCuster}

    def _next_alive_player(self, player: Player) -> Optional[Player]:
        """Return the next living player to the left."""
        if player not in self.players:
            return None
        idx = self.players.index(player)
        for i in range(1, len(self.players)):
            nxt = self.players[(idx + i) % len(self.players)]
            if nxt.is_alive():
                return nxt
        return None

    def _pass_left_or_discard(self, source: Player, card: BaseCard) -> None:
        """Pass card left if The River is active, else discard."""
        if self.event_flags.get("river"):
            target = self._next_alive_player(source)
            if target and target is not source:
                target.hand.append(card)
                return
        self.discard_pile.append(card)

    # ------------------------------------------------------------------
    # Turn management helpers
    def _current_player_obj(self) -> Player:
        """Return the Player instance whose turn it currently is."""
        return self.players[self.turn_order[self.current_turn]]

    def _reindex_turn_order(self, removed_idx: int) -> None:
        """Remove ``removed_idx`` from turn order and shift indices."""
        self.turn_order = [
            i - 1 if i > removed_idx else i for i in self.turn_order if i != removed_idx
        ]

    def _reset_current_turn(self, current_obj: Player | None) -> None:
        """Update ``current_turn`` after player removal."""
        if current_obj and current_obj in self.players:
            cur_idx = self.players.index(current_obj)
            if cur_idx in self.turn_order:
                self.current_turn = self.turn_order.index(cur_idx)
                return
        self.current_turn %= len(self.turn_order)

    def _get_player_by_index(self, idx: int) -> Optional[Player]:
        if 0 <= idx < len(self.players):
            return self.players[idx]
        return None

    def get_player_by_index(self, idx: int) -> Optional[Player]:
        """Return the player at ``idx`` if it exists."""
        return self._get_player_by_index(idx)

    def on_player_damaged(self, player: Player, source: Optional[Player] = None) -> None:
        self._notify_damage_listeners(player, source)
        if player.health > 0:
            return
        if self._handle_ghost_town_revive(player):
            return
        self._record_first_elimination(player)
        self._bounty_reward(source)
        self._notify_death_listeners(player, source)
        self._check_win_conditions()

    def _notify_damage_listeners(self, player: Player, source: Optional[Player]) -> None:
        for cb in self.player_damaged_listeners:
            cb(player, source)

    def _bounty_reward(self, source: Optional[Player]) -> None:
        if source and self.event_flags.get("bounty"):
            self.draw_card(source, 2)

    def _notify_death_listeners(self, player: Player, source: Optional[Player]) -> None:
        for cb in self.player_death_listeners:
            cb(player, source)

    def _handle_ghost_town_revive(self, player: Player) -> bool:
        """Revive a Ghost Town player if possible."""
        if self.event_flags.get("ghost_town") and player.metadata.ghost_revived:
            player.health = 1
            return True
        return False

    def _record_first_elimination(self, player: Player) -> None:
        if self.first_eliminated is None:
            self.first_eliminated = player

    def on_player_healed(self, player: Player) -> None:
        for cb in self.player_healed_listeners:
            cb(player)

    def blood_brothers_transfer(self, donor: Player, target: Player) -> bool:
        """Transfer one life from ``donor`` to ``target`` if allowed."""
        if not self.event_flags.get("blood_brothers"):
            return False
        if donor.health <= 1 or donor not in self.players or target not in self.players:
            return False
        donor.take_damage(1)
        self.on_player_damaged(donor)
        if not donor.is_alive():
            return True
        target.heal(1)
        self.on_player_healed(target)
        return True

    def _check_win_conditions(self) -> Optional[str]:
        alive = [p for p in self.players if p.is_alive()]
        self._update_turn_order_post_death()
        has_sheriff = any(isinstance(p.role, SheriffRoleCard) for p in self.players)
        result = self._determine_winner(alive, has_sheriff)
        if result:
            for cb in self.game_over_listeners:
                cb(result)
        return result

    # ------------------------------------------------------------------
    # Win condition helpers
    def _update_turn_order_post_death(self) -> None:
        """Remove eliminated players from turn order and adjust the index."""
        self.turn_order = [i for i in self.turn_order if self.players[i].is_alive()]
        if self.turn_order:
            self.current_turn %= len(self.turn_order)
        else:
            self.current_turn = 0

    def _determine_winner(self, alive: List[Player], has_sheriff: bool) -> Optional[str]:
        """Return a victory message if a win condition is met."""
        if not has_sheriff and len(self.players) == 3:
            if len(alive) == 1 and alive[0].role:
                return alive[0].role.victory_message
            return None
        for player in alive:
            if player.role and player.role.check_win(self, player):
                return player.role.victory_message
        return None

    def get_hand(self, viewer: Player, target: Player) -> list[str]:
        """Return the visible hand of ``target`` for ``viewer``."""
        if viewer is target or self.event_flags.get("revealed_hands"):
            return [c.card_name for c in target.hand]
        return ["?" for _ in target.hand]
