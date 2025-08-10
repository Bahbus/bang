"""Handlers for green (Dodge City) cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.howitzer import HowitzerCard
from ..cards.pony_express import PonyExpressCard
from ..cards.knife import KnifeCard
from ..cards.bible import BibleCard
from ..cards.canteen import CanteenCard
from ..cards.conestoga import ConestogaCard
from ..cards.can_can import CanCanCard
from ..cards.buffalo_rifle import BuffaloRifleCard
from ..cards.pepperbox import PepperboxCard
from ..cards.derringer import DerringerCard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


def register(game: "GameManager") -> None:
    """Register handlers for green cards on ``game``."""
    game._card_handlers.update(
        {
            HowitzerCard: game._handler_self_player_game,
            PonyExpressCard: game._handler_self_player_game,
            KnifeCard: game._handler_target_player_game,
            BibleCard: game._handler_target_or_self_player_game,
            CanteenCard: game._handler_target_or_self_player_game,
            ConestogaCard: game._handler_target_player_game,
            CanCanCard: game._handler_target_game,
            BuffaloRifleCard: game._handler_target_player_game,
            PepperboxCard: game._handler_target_player_game,
            DerringerCard: game._handler_target_player_game,
        }
    )
