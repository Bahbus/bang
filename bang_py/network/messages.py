"""Typed payload definitions for websocket communication."""

from __future__ import annotations

from typing import Literal, TypedDict


class DrawPayload(TypedDict, total=False):
    """Payload for drawing cards from the deck."""

    action: Literal["draw"]
    num: int


class DiscardPayload(TypedDict):
    """Payload for discarding a card from the player's hand."""

    action: Literal["discard"]
    card_index: int


class PlayCardPayload(TypedDict, total=False):
    """Payload for playing a card, optionally targeting another player."""

    action: Literal["play_card"]
    card_index: int
    target: int


class GeneralStorePickPayload(TypedDict):
    """Payload for choosing a card from the general store."""

    action: Literal["general_store_pick"]
    index: int


class UseAbilityPayload(TypedDict, total=False):
    """Payload for invoking a character ability."""

    action: Literal["use_ability"]
    ability: str
    indices: list[int]
    target: int
    card_index: int
    discard: int
    equipment: int
    card: int
    use_discard: bool
    enabled: bool


class SetAutoMissPayload(TypedDict, total=False):
    """Payload for toggling automatic responses to BANG! cards."""

    action: Literal["set_auto_miss"]
    enabled: bool


class SidKetchumPayload(TypedDict, total=False):
    indices: list[int]


class ChuckWengamPayload(TypedDict, total=False):
    pass


class DocHolydayPayload(TypedDict, total=False):
    indices: list[int]


class VeraCusterPayload(TypedDict, total=False):
    target: int


class JesseJonesPayload(TypedDict, total=False):
    target: int
    card_index: int


class KitCarlsonPayload(TypedDict, total=False):
    discard: int


class PedroRamirezPayload(TypedDict, total=False):
    use_discard: bool


class JoseDelgadoPayload(TypedDict, total=False):
    equipment: int


class PatBrennanPayload(TypedDict, total=False):
    target: int
    card: int


class LuckyDukePayload(TypedDict, total=False):
    card_index: int


class UncleWillPayload(TypedDict, total=False):
    card_index: int


__all__ = [
    "DrawPayload",
    "DiscardPayload",
    "PlayCardPayload",
    "GeneralStorePickPayload",
    "UseAbilityPayload",
    "SetAutoMissPayload",
    "SidKetchumPayload",
    "ChuckWengamPayload",
    "DocHolydayPayload",
    "VeraCusterPayload",
    "JesseJonesPayload",
    "KitCarlsonPayload",
    "PedroRamirezPayload",
    "JoseDelgadoPayload",
    "PatBrennanPayload",
    "LuckyDukePayload",
    "UncleWillPayload",
]
