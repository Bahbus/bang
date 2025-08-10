"""Handlers for basic (brown) cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.bang import BangCard
from ..cards.stagecoach import StagecoachCard
from ..cards.wells_fargo import WellsFargoCard
from ..cards.cat_balou import CatBalouCard
from ..cards.panic import PanicCard
from ..cards.indians import IndiansCard
from ..cards.duel import DuelCard
from ..cards.general_store import GeneralStoreCard
from ..cards.saloon import SaloonCard
from ..cards.gatling import GatlingCard
from ..cards.whisky import WhiskyCard
from ..cards.beer import BeerCard
from ..cards.tequila import TequilaCard
from ..cards.punch import PunchCard
from ..cards.brawl import BrawlCard
from ..cards.springfield import SpringfieldCard
from ..cards.rag_time import RagTimeCard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


def register(game: "GameManager") -> None:
    """Register handlers for basic cards on ``game``."""
    game._card_handlers.update(
        {
            BangCard: game._play_bang_card,
            StagecoachCard: game._handler_self_game,
            WellsFargoCard: game._handler_self_game,
            CatBalouCard: game._handler_target_game,
            PanicCard: game._handler_target_player_game,
            IndiansCard: game._handler_self_player_game,
            DuelCard: game._handler_target_player_game,
            GeneralStoreCard: game._handler_self_player_game,
            SaloonCard: game._handler_self_player_game,
            GatlingCard: game._handler_self_player_game,
            WhiskyCard: game._handler_target_or_self_player_game,
            BeerCard: game._handler_target_or_self_player_game,
            TequilaCard: game._handler_target_or_self_player_game,
            PunchCard: game._handler_target_player,
            BrawlCard: game._handler_self_player_game,
            SpringfieldCard: game._handler_target_player_game,
            RagTimeCard: game._handler_target_player_game,
        }
    )
