"""Typed definitions for event flag entries used across the game."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from .player import Player


class EventFlags(TypedDict, total=False):
    """Optional flags toggled by events and abilities."""

    abandoned_mine: bool
    ambush: bool
    bang_limit: int
    beer_heal: int
    blood_brothers: bool
    bounty: bool
    dead_man: bool
    dead_man_player: "Player"
    dead_man_used: bool
    draw_count: int
    fistful_of_cards: bool
    ghost_town: bool
    handcuffs: bool
    hard_liquor: bool
    judge: bool
    lasso: bool
    law_of_the_west: bool
    new_identity: bool
    no_abilities: bool
    no_bang: bool
    no_beer: bool
    no_beer_play: bool
    no_draw: bool
    no_jail: bool
    no_missed: bool
    peyote: bool
    peyote_bonus: int
    ranch: bool
    reverend_limit: int
    reverse_turn: bool
    ricochet: bool
    river: bool
    sniper: bool
    start_damage: int
    suit_override: str
    turn_suit: str
    vendetta: bool
    vendetta_used: set["Player"]
    revealed_hands: bool
    skip_turn: bool
