from __future__ import annotations

import random
from typing import List, Tuple, Type

from .deck import Deck
from .cards import (
    BangCard,
    BeerCard,
    MissedCard,
    VolcanicCard,
    SchofieldCard,
    RemingtonCard,
    CarbineCard,
    WinchesterCard,
    BarrelCard,
    ScopeCard,
    MustangCard,
    JailCard,
    DynamiteCard,
    StagecoachCard,
    WellsFargoCard,
    CatBalouCard,
    PanicCard,
    IndiansCard,
    DuelCard,
    GeneralStoreCard,
    SaloonCard,
    GatlingCard,
)
from .cards.card import Card


CARD_COUNTS: List[Tuple[Type[Card], int]] = [
    (BangCard, 25),
    (MissedCard, 12),
    (BeerCard, 6),
    (VolcanicCard, 1),
    (SchofieldCard, 3),
    (RemingtonCard, 1),
    (CarbineCard, 1),
    (WinchesterCard, 1),
    (BarrelCard, 2),
    (ScopeCard, 1),
    (MustangCard, 2),
    (JailCard, 3),
    (DynamiteCard, 1),
    (StagecoachCard, 2),
    (WellsFargoCard, 1),
    (CatBalouCard, 4),
    (PanicCard, 4),
    (IndiansCard, 2),
    (DuelCard, 3),
    (GeneralStoreCard, 2),
    (SaloonCard, 1),
    (GatlingCard, 1),
]


def _generate_suits(count: int) -> List[str]:
    """Return a shuffled list of suits with nearly even distribution."""
    base = count // 4
    extra = count % 4
    suits_pool: List[str] = []
    for i, suit in enumerate(["Hearts", "Diamonds", "Clubs", "Spades"]):
        suits_pool.extend([suit] * (base + (1 if i < extra else 0)))
    random.shuffle(suits_pool)
    return suits_pool


def create_standard_deck() -> Deck:
    """Return a Deck built with cards using a balanced suit distribution."""
    total = sum(c for _, c in CARD_COUNTS)
    suits = _generate_suits(total)
    ranks = list(range(1, 14)) * (total // 13 + 1)
    random.shuffle(ranks)

    cards: List[Card] = []
    idx = 0
    for card_cls, count in CARD_COUNTS:
        for _ in range(count):
            suit = suits[idx % len(suits)]
            rank = ranks[idx % len(ranks)]
            cards.append(card_cls(suit=suit, rank=rank))
            idx += 1

    return Deck(cards)
