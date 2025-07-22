"""Card play dispatch and handler utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .cards.bang import BangCard
from .cards.missed import MissedCard
from .cards.card import BaseCard
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
from .cards.whisky import WhiskyCard
from .cards.beer import BeerCard
from .cards.high_noon_card import HighNoonCard
from .cards.pony_express import PonyExpressCard
from .cards.tequila import TequilaCard
from .cards.punch import PunchCard
from .cards.knife import KnifeCard
from .cards.brawl import BrawlCard
from .cards.springfield import SpringfieldCard
from .cards.rag_time import RagTimeCard
from .cards.bible import BibleCard
from .cards.canteen import CanteenCard
from .cards.conestoga import ConestogaCard
from .cards.can_can import CanCanCard
from .cards.buffalo_rifle import BuffaloRifleCard
from .cards.pepperbox import PepperboxCard
from .cards.derringer import DerringerCard
from .helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from .game_manager import GameManager
    from .player import Player


class CardHandlersMixin:
    """Mixin implementing card play dispatch for ``GameManager``."""

    card_played_listeners: list
    discard_pile: list
    event_flags: dict
    _card_handlers: dict

    def _handler_self_game(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        card.play(player, game=self)

    def _handler_target_game(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        if target:
            card.play(target, game=self)

    def _handler_target_player_game(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        if target:
            card.play(target, player, game=self)

    def _handler_self_player_game(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        card.play(player, player, game=self)

    def _handler_target_or_self_player_game(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        card.play(target or player, player, game=self)

    def _handler_target_player(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        if target:
            card.play(target, player)

    def _play_bang_card(self: 'GameManager', player: 'Player', card: BangCard, target: Optional['Player']) -> None:
        ignore_eq = player.metadata.ignore_others_equipment
        extra_bang = self._consume_sniper_extra(player, card)
        need_two = player.metadata.double_miss or extra_bang
        if target and need_two:
            if not self._attempt_double_dodge(target):
                card.play(target, self.deck, ignore_equipment=ignore_eq)
        else:
            if not (target and self._auto_miss(target)):
                card.play(target, self.deck, ignore_equipment=ignore_eq)

    def _consume_sniper_extra(self: 'GameManager', player: 'Player', card: BangCard) -> bool:
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

    def _attempt_double_dodge(self: 'GameManager', target: 'Player') -> bool:
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

    def _register_card_handlers(self: 'GameManager') -> None:
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

    def _dispatch_play(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> None:
        if self._handle_missed_as_bang(player, card, target):
            return
        handler = self._card_handlers.get(type(card))
        if handler:
            handler(player, card, target)
        else:
            card.play(target)

    def _handle_missed_as_bang(self: 'GameManager', player: 'Player', card: BaseCard, target: Optional['Player']) -> bool:
        if player.metadata.play_missed_as_bang and isinstance(card, MissedCard) and target:
            handler = self._card_handlers.get(BangCard)
            if handler:
                handler(player, BangCard(), target)
            return True
        return False
