from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import random

from .deck import Deck
from .deck_factory import create_standard_deck
from .cards.card import BaseCard
from .helpers import has_ability, handle_out_of_turn_discard
from .characters.chuck_wengam import ChuckWengam
from .characters.doc_holyday import DocHolyday
from .characters.jesse_jones import JesseJones
from .characters.jose_delgado import JoseDelgado
from .characters.kit_carlson import KitCarlson
from .characters.pat_brennan import PatBrennan
from .characters.pedro_ramirez import PedroRamirez
from .characters.sid_ketchum import SidKetchum
from .characters.uncle_will import UncleWill
from .characters.vera_custer import VeraCuster
from .characters.sean_mallory import SeanMallory
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
from .cards.ten_gallon_hat import TenGallonHatCard
from .cards.rev_carabine import RevCarabineCard
from .cards.buffalo_rifle import BuffaloRifleCard
from .cards.pepperbox import PepperboxCard
from .cards.derringer import DerringerCard

from .player import Player, Role
from .event_decks import (
    EventCard,
    create_high_noon_deck,
    create_fistful_deck,
)


@dataclass
class GameManager:
    """Manage players, deck and discard pile while controlling turn order and
    triggering game events."""

    players: List[Player] = field(default_factory=list)
    deck: Deck | None = None
    expansions: List[str] = field(default_factory=list)
    discard_pile: List[BaseCard] = field(default_factory=list)
    current_turn: int = 0
    turn_order: List[int] = field(default_factory=list)
    event_deck: List[EventCard] | None = None
    current_event: EventCard | None = None
    event_flags: dict = field(default_factory=dict)

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
    card_play_checks: List[Callable[[Player, BaseCard, Optional[Player]], bool]] = field(default_factory=list)
    card_played_listeners: List[Callable[[Player, BaseCard, Optional[Player]], None]] = field(default_factory=list)
    _duel_counts: dict | None = field(default=None, init=False, repr=False)

    def draw_event_card(self) -> None:
        """Draw and apply the next event card."""
        if not self.event_deck:
            return
        self.current_event = self.event_deck.pop(0)
        self.event_flags.clear()
        self.current_event.apply(self)

    def __post_init__(self) -> None:
        if self.deck is None:
            if not self.expansions:
                self.expansions.append("dodge_city")
            self.deck = create_standard_deck(self.expansions)
        self.event_flags = {}
        if "high_noon" in self.expansions:
            self.event_deck = create_high_noon_deck()
            if self.event_deck:
                final = next((c for c in self.event_deck if c.name == "High Noon"), None)
                if final:
                    self.event_deck.remove(final)
                    random.shuffle(self.event_deck)
                    self.event_deck.append(final)
        elif "fistful_of_cards" in self.expansions:
            self.event_deck = create_fistful_deck()
            if self.event_deck:
                final = next((c for c in self.event_deck if c.name == "A Fistful of Cards"), None)
                if final:
                    self.event_deck.remove(final)
                    random.shuffle(self.event_deck)
                    self.event_deck.append(final)
        elif self.event_deck:
            random.shuffle(self.event_deck)
        self._register_card_handlers()

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

        # Track the current player object to preserve turn position when
        # possible.
        current_obj: Player | None = None
        if self.turn_order:
            current_obj = self.players[self.turn_order[self.current_turn]]

        idx = self.players.index(player)
        self.players.pop(idx)
        player.metadata.game = None

        new_order: List[int] = []
        for order_idx in self.turn_order:
            if order_idx == idx:
                continue
            if order_idx > idx:
                new_order.append(order_idx - 1)
            else:
                new_order.append(order_idx)
        self.turn_order = new_order

        if not self.turn_order:
            self.current_turn = 0
            return

        if current_obj and current_obj in self.players:
            cur_idx = self.players.index(current_obj)
            if cur_idx in self.turn_order:
                self.current_turn = self.turn_order.index(cur_idx)
                return

        self.current_turn %= len(self.turn_order)

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
        self.current_turn %= len(self.turn_order)
        idx = self.turn_order[self.current_turn]
        player = self.players[idx]
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)
        self.reset_turn_flags(player)
        pre_ghost = self.event_flags.get("ghost_town")
        if self.event_deck and player.role == Role.SHERIFF:
            self.draw_event_card()
            if pre_ghost:
                removed = False
                for pl in self.players:
                    if pl.metadata.ghost_revived and pl.is_alive():
                        pl.health = 0
                        pl.metadata.ghost_revived = False
                        removed = True
                if removed:
                    self.turn_order = [
                        i for i, pl in enumerate(self.players) if pl.is_alive()
                    ]
                    self.current_turn = self.turn_order.index(self.players.index(player))
                    idx = self.turn_order[self.current_turn]
                    player = self.players[idx]
        if self.event_flags.get("skip_turn"):
            self.event_flags.pop("skip_turn")
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
            self._begin_turn()
            return
        dmg = self.event_flags.get("start_damage", 0)
        if dmg:
            player.take_damage(dmg)
            self.on_player_damaged(player)
            if not player.is_alive():
                self._begin_turn()
                return
        if self.event_flags.get("damage_by_hand"):
            dmg = len(player.hand)
            if dmg:
                player.take_damage(dmg)
                self.on_player_damaged(player)
                if not player.is_alive():
                    self._begin_turn()
                    return
        # Handle start-of-turn equipment effects
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
                    return
        jail = player.equipment.get("Jail")
        if jail:
            if self.event_flags.get("no_jail"):
                player.equipment.pop("Jail", None)
                self.discard_pile.append(jail)
            elif getattr(jail, "check_turn", None):
                skipped = jail.check_turn(player, self.deck)
                self.discard_pile.append(jail)
                if skipped:
                    self.current_turn = (self.current_turn + 1) % len(self.turn_order)
                    self._begin_turn()
                    return


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
            return

        self.draw_phase(player)
        player.metadata.bangs_played = 0
        for cb in self.turn_started_listeners:
            cb(player)

    def end_turn(self) -> None:
        if not self.turn_order:
            return
        idx = self.turn_order[self.current_turn]
        player = self.players[idx]
        self.discard_phase(player)
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)
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
        bonus = int(self.event_flags.get("peyote_bonus", 0))
        for _ in range(num + bonus):
            card = self._draw_from_deck()
            if card:
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
    ) -> None:
        """Handle the draw phase for ``player`` with optional choices.

        Parameters allow callers to specify selections for characters with
        draw-phase abilities. If a parameter is ``None`` the default behavior of
        the ability is used.
        """

        if self.event_flags.get("doctor"):
            player.heal(1)
            return

        custom_draw = self.event_flags.get("draw_count")
        if custom_draw is not None:
            self.draw_card(player, custom_draw)
            return

        for cb in self.draw_phase_listeners:
            if cb(player, {
                "jesse_target": jesse_target,
                "jesse_card": jesse_card,
                "kit_back": kit_back,
                "pedro_use_discard": pedro_use_discard,
                "jose_equipment": jose_equipment,
                "pat_target": pat_target,
                "pat_card": pat_card,
            }):
                return

        self.draw_card(player, 2)

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
            self._pass_left_or_discard(player, card)

    def _pre_card_checks(
        self, player: Player, card: Card, target: Optional[Player]
    ) -> bool:
        if card not in player.hand:
            return False
        for cb in self.card_play_checks:
            if not cb(player, card, target):
                return False
        if (
            isinstance(card, BangCard)
            and target
            and player.distance_to(target) > player.attack_range
        ):
            return False
        if isinstance(card, PanicCard) and target and player.distance_to(target) > 1:
            return False
        if isinstance(card, JailCard) and target and target.role == Role.SHERIFF:
            return False
        if self.event_flags.get("no_jail") and isinstance(card, JailCard):
            return False
        return True

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
        if player.metadata.play_missed_as_bang and isinstance(card, MissedCard) and target:
            handler = self._card_handlers.get(BangCard)
            if handler:
                handler(player, BangCard(), target)
            return
        handler = self._card_handlers.get(type(card))
        if handler:
            handler(player, card, target)
        else:
            card.play(target)

    def _play_bang_card(self, player: Player, card: BangCard, target: Optional[Player]) -> None:
        ignore_eq = player.metadata.ignore_others_equipment
        if target and player.metadata.double_miss:
            misses = [c for c in target.hand if isinstance(c, MissedCard)]
            if len(misses) >= 2:
                for _ in range(2):
                    mcard = misses.pop()
                    target.hand.remove(mcard)
                    self.discard_pile.append(mcard)
                    handle_out_of_turn_discard(self, target, mcard)
                target.metadata.dodged = True
            else:
                card.play(target, self.deck, ignore_equipment=ignore_eq)
        else:
            if not (target and self._auto_miss(target)):
                card.play(target, self.deck, ignore_equipment=ignore_eq)
        if self.event_flags.get("ricochet") and target:
            extra = self._next_alive_player(target)
            if extra and extra not in (target, player):
                before_x = extra.health
                if not self._auto_miss(extra):
                    BangCard().play(extra, self.deck, ignore_equipment=ignore_eq)
                if extra.health < before_x:
                    self.on_player_damaged(extra, player)
                if extra.health > before_x:
                    self.on_player_healed(extra)

    def _handler_self_game(self, player: Player, card: BaseCard, target: Optional[Player]) -> None:
        """Play the card on the acting player with game context."""
        card.play(player, game=self)

    def _handler_target_game(self, player: Player, card: BaseCard, target: Optional[Player]) -> None:
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
        for cb in self.card_played_listeners:
            cb(player, card, target)
        if target and before is not None and target.health < before:
            self.on_player_damaged(target, player)
        if target and before is not None and target.health > before:
            self.on_player_healed(target)
        self._pass_left_or_discard(player, card)
        if is_bang:
            if player.metadata.doc_free_bang > 0:
                player.metadata.doc_free_bang -= 1
            else:
                player.metadata.bangs_played += 1
        if player.metadata.draw_when_empty and not player.hand:
            self.draw_card(player)

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
        if self.event_flags.get("no_missed"):
            return False
        if target.metadata.auto_miss is False:
            return False
        miss = next((c for c in target.hand if isinstance(c, MissedCard)), None)
        if miss:
            target.hand.remove(miss)
            self._pass_left_or_discard(target, miss)
            if not self.event_flags.get("river"):
                handle_out_of_turn_discard(self, target, miss)
            target.metadata.dodged = True
            return True
        if target.metadata.bang_as_missed:
            bang = next((c for c in target.hand if isinstance(c, BangCard)), None)
            if bang:
                target.hand.remove(bang)
                self._pass_left_or_discard(target, bang)
                if not self.event_flags.get("river"):
                    handle_out_of_turn_discard(self, target, bang)
                target.metadata.dodged = True
                return True
        if target.metadata.any_card_as_missed and target.hand:
            card = target.hand.pop()
            self._pass_left_or_discard(target, card)
            if not self.event_flags.get("river"):
                handle_out_of_turn_discard(self, target, card)
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

    # General Store management
    def start_general_store(self, player: Player) -> List[str]:
        """Draw cards for General Store and record selection order."""
        if not self.deck:
            return []
        alive = [p for p in self.players if p.is_alive()]
        cards: List[BaseCard] = []
        for _ in range(len(alive)):
            card = self._draw_from_deck()
            if card:
                cards.append(card)
        self.general_store_cards = cards
        start_idx = self.players.index(player)
        order: List[Player] = []
        for i in range(len(self.players)):
            p = self.players[(start_idx + i) % len(self.players)]
            if p.is_alive():
                order.append(p)
        self.general_store_order = order
        self.general_store_index = 0
        return [c.card_name for c in cards]

    def general_store_pick(self, player: Player, index: int) -> bool:
        """Give the chosen card to the current player."""
        if (
            self.general_store_cards is None
            or self.general_store_order is None
            or self.general_store_index >= len(self.general_store_order)
            or self.general_store_order[self.general_store_index] is not player
        ):
            return False
        if not (0 <= index < len(self.general_store_cards)):
            return False
        card = self.general_store_cards.pop(index)
        player.hand.append(card)
        self.general_store_index += 1
        if self.general_store_index >= len(self.general_store_order):
            for leftover in self.general_store_cards:
                self.discard_pile.append(leftover)
            self.general_store_cards = None
            self.general_store_order = None
            self.general_store_index = 0
        return True

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

    def _get_player_by_index(self, idx: int) -> Optional[Player]:
        if 0 <= idx < len(self.players):
            return self.players[idx]
        return None

    def on_player_damaged(self, player: Player, source: Optional[Player] = None) -> None:
        for cb in self.player_damaged_listeners:
            cb(player, source)
        if player.health <= 0:
            if source and self.event_flags.get("bounty"):
                self.draw_card(source, 2)
            for cb in self.player_death_listeners:
                cb(player, source)
            self._check_win_conditions()

    def on_player_healed(self, player: Player) -> None:
        for cb in self.player_healed_listeners:
            cb(player)

    def _check_win_conditions(self) -> Optional[str]:
        alive = [p for p in self.players if p.is_alive()]
        self.turn_order = [i for i in self.turn_order if self.players[i].is_alive()]
        if self.turn_order:
            self.current_turn %= len(self.turn_order)
        else:
            self.current_turn = 0
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
