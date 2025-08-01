"""Manage overall game state and turn progression for Bang."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence
import random

from .deck import Deck
from .deck_factory import create_standard_deck
from .cards.card import BaseCard
from .helpers import handle_out_of_turn_discard
from .event_logic import EventLogicMixin
from .card_handlers import CardHandlersMixin
from .general_store import GeneralStoreMixin
from .turn_phases import TurnPhasesMixin
from .characters.vera_custer import VeraCuster
from .cards.bang import BangCard
from .cards.missed import MissedCard
from .cards.general_store import GeneralStoreCard


from .player import Player
from .cards.roles import (
    BaseRole,
    DeputyRoleCard,
    OutlawRoleCard,
    RenegadeRoleCard,
    SheriffRoleCard,
)
from .characters.base import BaseCharacter
from .event_decks import EventCard
@dataclass
class GameManager(EventLogicMixin, CardHandlersMixin, GeneralStoreMixin, TurnPhasesMixin):
    """Manage players, deck and discard pile.

    Controls turn order and triggers game events.
    """

    _players: List[Player] = field(default_factory=list)
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

    @property
    def players(self) -> Sequence[Player]:
        """Players in turn order as a read-only sequence."""
        return tuple(self._players)

    def prompt_new_identity(self, player: Player) -> bool:
        """Return True if the player opts to switch characters."""
        return True


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


    def add_player(self, player: Player) -> None:
        """Add a player to the game and record the game reference."""
        player.metadata.game = self
        self._players.append(player)
        if player.character is not None:
            player.character.ability(self, player)

    def remove_player(self, player: Player) -> None:
        """Remove ``player`` from the game and update turn order."""
        if player not in self._players:
            return

        current_obj = self._current_player_obj() if self.turn_order else None

        idx = self._players.index(player)
        self._players.pop(idx)
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
        self.turn_order = list(range(len(self._players)))
        self.current_turn = 0
        # Deal initial hands
        for _ in range(2):
            for player in self._players:
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
        classes = role_map.get(len(self._players))
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


    def _deal_roles_and_characters(self) -> None:
        role_deck = self._build_role_deck()
        random.shuffle(role_deck)
        char_deck = [cls() for cls in self._build_character_deck()]
        random.shuffle(char_deck)

        for player in self._players:
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
        targets = [t for t in self._players if t is not player]
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


    def reset_turn_flags(self, player: Player) -> None:
        """Clear per-turn ability flags on ``player``."""
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
        if player not in self._players:
            return None
        idx = self._players.index(player)
        for i in range(1, len(self._players)):
            nxt = self._players[(idx + i) % len(self._players)]
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
        return self._players[self.turn_order[self.current_turn]]

    def _reindex_turn_order(self, removed_idx: int) -> None:
        """Remove ``removed_idx`` from turn order and shift indices."""
        self.turn_order = [
            i - 1 if i > removed_idx else i for i in self.turn_order if i != removed_idx
        ]

    def _reset_current_turn(self, current_obj: Player | None) -> None:
        """Update ``current_turn`` after player removal."""
        if current_obj and current_obj in self._players:
            cur_idx = self._players.index(current_obj)
            if cur_idx in self.turn_order:
                self.current_turn = self.turn_order.index(cur_idx)
                return
        self.current_turn %= len(self.turn_order)

    def _get_player_by_index(self, idx: int) -> Optional[Player]:
        if 0 <= idx < len(self._players):
            return self._players[idx]
        return None

    def get_player_by_index(self, idx: int) -> Optional[Player]:
        """Return the player at ``idx`` if it exists."""
        return self._get_player_by_index(idx)

    def on_player_damaged(self, player: Player, source: Optional[Player] = None) -> None:
        """Handle player damage and determine if they are eliminated."""
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
        """Notify listeners that ``player`` has regained health."""
        for cb in self.player_healed_listeners:
            cb(player)

    def blood_brothers_transfer(self, donor: Player, target: Player) -> bool:
        """Transfer one life from ``donor`` to ``target`` if allowed."""
        if not self.event_flags.get("blood_brothers"):
            return False
        if donor.health <= 1 or donor not in self._players or target not in self._players:
            return False
        donor.take_damage(1)
        self.on_player_damaged(donor)
        if not donor.is_alive():
            return True
        target.heal(1)
        self.on_player_healed(target)
        return True

    def _check_win_conditions(self) -> Optional[str]:
        alive = [p for p in self._players if p.is_alive()]
        self._update_turn_order_post_death()
        has_sheriff = any(isinstance(p.role, SheriffRoleCard) for p in self._players)
        result = self._determine_winner(alive, has_sheriff)
        if result:
            for cb in self.game_over_listeners:
                cb(result)
        return result

    # ------------------------------------------------------------------
    # Win condition helpers
    def _update_turn_order_post_death(self) -> None:
        """Remove eliminated players from turn order and adjust the index."""
        self.turn_order = [i for i in self.turn_order if self._players[i].is_alive()]
        if self.turn_order:
            self.current_turn %= len(self.turn_order)
        else:
            self.current_turn = 0

    def _determine_winner(self, alive: List[Player], has_sheriff: bool) -> Optional[str]:
        """Return a victory message if a win condition is met."""
        if not has_sheriff and len(self._players) == 3:
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
