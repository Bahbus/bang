from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import random

from .deck import Deck
from .deck_factory import create_standard_deck
from .cards.card import Card
from .helpers import has_ability, handle_out_of_turn_discard
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
    SlabTheKiller,
    SuzyLafayette,
    VultureSam,
    WillyTheKid,
    PixiePete,
    JoseDelgado,
    SeanMallory,
    TequilaJoe,
    VeraCuster,
    ApacheKid,
    GregDigger,
    BelleStar,
    BillNoface,
    ChuckWengam,
    DocHolyday,
    ElenaFuente,
    HerbHunter,
    PatBrennan,
    UncleWill,
    MollyStark,
    JohnnyKisch,
    ClausTheSaint,
)
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
from .cards.punch import PunchCard
from .cards.whisky import WhiskyCard
from .cards.beer import BeerCard
from .cards.high_noon_card import HighNoonCard
from .cards.pony_express import PonyExpressCard
from .cards.tequila import TequilaCard

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
    discard_pile: List[Card] = field(default_factory=list)
    current_turn: int = 0
    turn_order: List[int] = field(default_factory=list)
    event_deck: List[EventCard] | None = None
    current_event: EventCard | None = None
    event_flags: dict = field(default_factory=dict)

    # General Store state
    general_store_cards: List[Card] | None = None
    general_store_order: List[Player] | None = None
    general_store_index: int = 0

    # Event listeners
    player_damaged_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    player_healed_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    turn_started_listeners: List[Callable[[Player], None]] = field(default_factory=list)
    game_over_listeners: List[Callable[[str], None]] = field(default_factory=list)

    def draw_event_card(self) -> None:
        """Draw and apply the next event card."""
        if not self.event_deck:
            return
        random.shuffle(self.event_deck)
        self.current_event = self.event_deck.pop(0)
        self.event_flags.clear()
        self.current_event.apply(self)

    def __post_init__(self) -> None:
        if self.deck is None:
            self.deck = create_standard_deck(self.expansions)
        self.event_flags = {}
        if "high_noon" in self.expansions:
            self.event_deck = create_high_noon_deck()
        elif "fistful_of_cards" in self.expansions:
            self.event_deck = create_fistful_deck()

    def add_player(self, player: Player) -> None:
        """Add a player to the game and record the game reference."""
        player.metadata["game"] = self
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
        self.current_turn %= len(self.turn_order)
        idx = self.turn_order[self.current_turn]
        player = self.players[idx]
        self.reset_turn_flags(player)
        if self.event_deck and player.role == Role.SHERIFF:
            self.draw_event_card()
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
            LuckyDuke,
        )

        if isinstance(player.character, ability_chars):
            player.metadata["awaiting_draw"] = True
            for cb in self.turn_started_listeners:
                cb(player)
            return

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

    def draw_phase(
        self,
        player: Player,
        *,
        jesse_target: Player | None = None,
        kit_discard: int | None = None,
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

        custom_draw = self.event_flags.get("draw_count")
        if custom_draw is not None:
            self.draw_card(player, custom_draw)
            return
        char = player.character
        if isinstance(char, JesseJones):
            opponents = [p for p in self.players if p is not player and p.hand]
            if opponents:
                source = jesse_target if jesse_target in opponents else random.choice(opponents)
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
            keep_cards = []
            for i, c in enumerate(cards):
                if c is None:
                    continue
                if kit_discard is not None and i == kit_discard:
                    self.discard_pile.append(c)
                elif len(keep_cards) < 2:
                    keep_cards.append(c)
                else:
                    self.discard_pile.append(c)
            for c in keep_cards:
                player.hand.append(c)
            return
        if isinstance(char, PedroRamirez) and self.discard_pile:
            if pedro_use_discard is False:
                self.draw_card(player, 2)
            else:
                player.hand.append(self.discard_pile.pop())
                self.draw_card(player)
            return
        if isinstance(char, PixiePete):
            self.draw_card(player, 3)
            return
        if isinstance(char, JoseDelgado):
            equips = [c for c in player.hand if hasattr(c, "slot")]
            equip = None
            if jose_equipment is not None and 0 <= jose_equipment < len(equips):
                equip = equips[jose_equipment]
            elif equips:
                equip = equips[0]
            if equip:
                player.hand.remove(equip)
                self.discard_pile.append(equip)
                self.draw_card(player, 2)
            self.draw_card(player)
            return
        if isinstance(char, BillNoface):
            wounds = player.max_health - player.health
            self.draw_card(player, 1 + wounds)
            return
        if isinstance(char, PatBrennan):
            if not self.pat_brennan_draw(player, pat_target, pat_card):
                self.draw_card(player)
            self.draw_card(player)
            return
        if isinstance(char, ClausTheSaint):
            alive = [p for p in self.players if p.is_alive()]
            cards = []
            for _ in range(len(alive) + 1):
                card = self.deck.draw()
                if card:
                    cards.append(card)
            keep = cards[:2]
            for c in keep:
                player.hand.append(c)
            others = [p for p in alive if p is not player]
            idx = 2
            for p in others:
                if idx < len(cards):
                    p.hand.append(cards[idx])
                    idx += 1
            return
        self.draw_card(player, 2)

    def discard_phase(self, player: Player) -> None:
        """Discard down to the player's hand limit at the end of their turn."""
        limit = player.health
        if has_ability(player, SeanMallory):
            limit = 99
        while len(player.hand) > limit:
            card = player.hand.pop()
            self.discard_pile.append(card)

    def play_card(self, player: Player, card: Card, target: Optional[Player] = None) -> None:
        if card not in player.hand:
            return
        if target and has_ability(target, ApacheKid):
            if getattr(card, "suit", None) == "Diamonds":
                player.hand.remove(card)
                self.discard_pile.append(card)
                return
        if isinstance(card, BangCard) and target:
            if player.distance_to(target) > player.attack_range:
                return
        if isinstance(card, PanicCard) and target:
            if player.distance_to(target) > 1:
                return
        if isinstance(card, JailCard) and target and target.role == Role.SHERIFF:
            return
        if self.event_flags.get("no_jail") and isinstance(card, JailCard):
            return
        # Determine if this card counts as a Bang!
        is_bang = isinstance(card, BangCard) or (
            has_ability(player, CalamityJanet) and isinstance(card, MissedCard) and target
        )
        if is_bang:
            if self.event_flags.get("no_bang"):
                return
            count = int(player.metadata.get("bangs_played", 0))
            gun = player.equipment.get("Gun")
            extra = int(player.metadata.get("doc_free_bang", 0))
            unlimited = (
                has_ability(player, WillyTheKid)
                or getattr(gun, "unlimited_bang", False)
                or extra > 0
            )
            limit = self.event_flags.get("bang_limit", 1)
            if count >= limit and not unlimited:
                # Cannot play more Bang! cards this turn
                return
        player.hand.remove(card)
        before = target.health if target else None
        if has_ability(player, CalamityJanet) and isinstance(card, MissedCard) and target:
            BangCard().play(target, self.deck)
        elif isinstance(card, BangCard):
            ignore_eq = has_ability(player, BelleStar)
            if target and has_ability(player, SlabTheKiller):
                misses = [c for c in target.hand if isinstance(c, MissedCard)]
                if len(misses) >= 2:
                    for _ in range(2):
                        mcard = misses.pop()
                        target.hand.remove(mcard)
                        self.discard_pile.append(mcard)
                        handle_out_of_turn_discard(self, target, mcard)
                    target.metadata["dodged"] = True
                else:
                    card.play(target, self.deck, ignore_equipment=ignore_eq)
            else:
                if target and self._auto_miss(target):
                    pass
                else:
                    card.play(target, self.deck, ignore_equipment=ignore_eq)
        elif isinstance(card, StagecoachCard):
            self.draw_card(player, 2)
        elif isinstance(card, WellsFargoCard):
            self.draw_card(player, 3)
        elif isinstance(card, CatBalouCard) and target:
            card.play(target, game=self)
        elif isinstance(card, PanicCard) and target:
            card.play(target, player, game=self)
        elif isinstance(card, IndiansCard):
            card.play(player, player, game=self)
        elif isinstance(card, DuelCard) and target:
            card.play(target, player, game=self)
        elif isinstance(card, GeneralStoreCard):
            card.play(player, player, game=self)
        elif isinstance(card, SaloonCard):
            card.play(player, player, game=self)
        elif isinstance(card, GatlingCard):
            card.play(player, player, game=self)
        elif isinstance(card, WhiskyCard):
            card.play(target or player, player, game=self)
        elif isinstance(card, BeerCard):
            before_hp = (target or player).health
            card.play(target or player)
            if (
                has_ability(player, TequilaJoe)
                and (target or player).health < (target or player).max_health
            ):
                (target or player).heal(1)
            if (target or player).health > before_hp:
                self.on_player_healed(target or player)
        elif isinstance(card, PonyExpressCard):
            card.play(player, player, game=self)
        elif isinstance(card, TequilaCard):
            card.play(target or player, player, game=self)
        elif isinstance(card, HighNoonCard):
            card.play(player, player, game=self)
        elif isinstance(card, PunchCard) and target:
            card.play(target, player)
        else:
            card.play(target)
        if has_ability(player, JohnnyKisch) and hasattr(card, "card_name"):
            for p in self.players:
                if p is player:
                    continue
                other = p.unequip(card.card_name)
                if other:
                    self.discard_pile.append(other)
        if target and before is not None and target.health < before:
            self.on_player_damaged(target, player)
        if target and before is not None and target.health > before:
            self.on_player_healed(target)
        self.discard_pile.append(card)
        if is_bang:
            if int(player.metadata.get("doc_free_bang", 0)) > 0:
                player.metadata["doc_free_bang"] -= 1
            else:
                player.metadata["bangs_played"] = int(player.metadata.get("bangs_played", 0)) + 1
        if has_ability(player, SuzyLafayette) and not player.hand:
            self.draw_card(player)

    def discard_card(self, player: Player, card: Card) -> None:
        if card in player.hand:
            player.hand.remove(card)
            self.discard_pile.append(card)
            handle_out_of_turn_discard(self, player, card)
            if has_ability(player, SuzyLafayette) and not player.hand:
                self.draw_card(player)

    def sid_ketchum_ability(self, player: Player, indices: List[int] | None = None) -> None:
        if not has_ability(player, SidKetchum):
            return
        if len(player.hand) < 2 or player.health >= player.max_health:
            return
        discard_indices = indices or list(range(2))
        discard_indices = sorted(discard_indices, reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                self.discard_pile.append(card)
        player.heal(1)
        self.on_player_healed(player)

    def _auto_miss(self, target: Player) -> bool:
        if self.event_flags.get("no_missed"):
            return False
        miss = next((c for c in target.hand if isinstance(c, MissedCard)), None)
        if miss:
            target.hand.remove(miss)
            self.discard_pile.append(miss)
            handle_out_of_turn_discard(self, target, miss)
            target.metadata["dodged"] = True
            return True
        if has_ability(target, CalamityJanet):
            bang = next((c for c in target.hand if isinstance(c, BangCard)), None)
            if bang:
                target.hand.remove(bang)
                self.discard_pile.append(bang)
                handle_out_of_turn_discard(self, target, bang)
                target.metadata["dodged"] = True
                return True
        if has_ability(target, ElenaFuente) and target.hand:
            card = target.hand.pop()
            self.discard_pile.append(card)
            handle_out_of_turn_discard(self, target, card)
            target.metadata["dodged"] = True
            return True
        return False

    def chuck_wengam_ability(self, player: Player) -> None:
        """Lose 1 life to draw 2 cards, usable multiple times per turn."""
        if not has_ability(player, ChuckWengam):
            return
        if player.health <= 1:
            return
        player.take_damage(1)
        self.on_player_damaged(player)
        self.draw_card(player, 2)

    def doc_holyday_ability(self, player: Player, indices: List[int] | None = None) -> None:
        """Discard two cards to gain a Bang! that doesn't count toward the limit."""
        if not has_ability(player, DocHolyday):
            return
        if player.metadata.get("doc_used"):
            return
        if len(player.hand) < 2:
            return
        discard_indices = indices or list(range(2))
        discard_indices = sorted(discard_indices, reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                self.discard_pile.append(card)
        player.metadata["doc_used"] = True
        player.metadata["doc_free_bang"] = int(player.metadata.get("doc_free_bang", 0)) + 1
        player.hand.append(BangCard())

    def pat_brennan_draw(
        self,
        player: Player,
        target: Player | None = None,
        card_name: str | None = None,
    ) -> bool:
        """During draw phase, draw a card in play instead of from deck."""
        if not has_ability(player, PatBrennan):
            return False
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

    def uncle_will_ability(self, player: Player, card: Card) -> bool:
        """Play any card as General Store once per turn."""
        if not has_ability(player, UncleWill):
            return False
        if player.metadata.get("uncle_used"):
            return False
        player.metadata["uncle_used"] = True
        GeneralStoreCard().play(player, player, game=self)
        player.hand.remove(card)
        self.discard_pile.append(card)
        return True

    def vera_custer_copy(self, player: Player, target: Player) -> None:
        """Copy another living character's ability for the turn."""
        if not isinstance(player.character, VeraCuster):
            return
        if not target.is_alive() or target is player:
            return
        player.metadata["vera_copy"] = target.character.__class__

    # General Store management
    def start_general_store(self, player: Player) -> List[str]:
        """Draw cards for General Store and record selection order."""
        if not self.deck:
            return []
        alive = [p for p in self.players if p.is_alive()]
        cards: List[Card] = []
        for _ in range(len(alive)):
            card = self.deck.draw()
            if card is None:
                if self.discard_pile:
                    self.deck.cards.extend(self.discard_pile)
                    self.discard_pile.clear()
                    random.shuffle(self.deck.cards)
                    card = self.deck.draw()
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
        player.metadata.pop("doc_used", None)
        player.metadata.pop("doc_free_bang", None)
        player.metadata.pop("uncle_used", None)
        if isinstance(player.character, VeraCuster):
            player.metadata.pop("vera_copy", None)

    def _get_player_by_index(self, idx: int) -> Optional[Player]:
        if 0 <= idx < len(self.players):
            return self.players[idx]
        return None

    def on_player_damaged(self, player: Player, source: Optional[Player] = None) -> None:
        for cb in self.player_damaged_listeners:
            cb(player)
        if has_ability(player, BartCassidy):
            self.draw_card(player)
        if has_ability(player, ElGringo) and source and source.hand:
            stolen = random.choice(source.hand)
            source.hand.remove(stolen)
            player.hand.append(stolen)
        if player.health <= 0:
            for p in self.players:
                if has_ability(p, GregDigger) and p.is_alive():
                    before = p.health
                    p.heal(2)
                    if p.health > before:
                        self.on_player_healed(p)
            for p in self.players:
                if p is not player and has_ability(p, HerbHunter):
                    self.draw_card(p, 2)
            for p in self.players:
                if p is not player and has_ability(p, VultureSam):
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
