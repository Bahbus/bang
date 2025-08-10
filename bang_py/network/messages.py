"""Typed payload definitions for websocket communication."""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class DrawPayload(TypedDict, total=False):
    """Payload for drawing cards from the deck."""

    action: Literal["draw"]
    num: NotRequired[int]


class DiscardPayload(TypedDict):
    """Payload for discarding a card from the player's hand."""

    action: Literal["discard"]
    card_index: int


class PlayCardPayload(TypedDict, total=False):
    """Payload for playing a card, optionally targeting another player."""

    action: Literal["play_card"]
    card_index: int
    target: NotRequired[int]


class UseAbilityPayload(TypedDict, total=False):
    """Payload for invoking a character ability."""

    action: Literal["use_ability"]
    ability: str
    indices: NotRequired[list[int]]
    target: NotRequired[int]
    card_index: NotRequired[int]
    discard: NotRequired[int]
    equipment: NotRequired[int]
    card: NotRequired[int]
    use_discard: NotRequired[bool]
    enabled: NotRequired[bool]


class SetAutoMissPayload(TypedDict):
    """Payload for toggling automatic responses to Bang! cards."""

    action: Literal["set_auto_miss"]
    enabled: bool


__all__ = [
    "DrawPayload",
    "DiscardPayload",
    "PlayCardPayload",
    "UseAbilityPayload",
    "SetAutoMissPayload",
]
