from __future__ import annotations

import random
from typing import Iterable, List, Tuple, Type

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
    PunchCard,
    HideoutCard,
    BinocularsCard,
    BuffaloRifleCard,
    KnifeCard,
    BrawlCard,
    SpringfieldCard,
    WhiskyCard,
    HighNoonCard,
    SombreroCard,
    IronPlateCard,
    TequilaCard,
    PonyExpressCard,
    DerringerCard,
    RagTimeCard,
    PepperboxCard,
    HowitzerCard,
    BibleCard,
    CanteenCard,
    ConestogaCard,
    CanCanCard,
    TenGallonHatCard,
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

# Additional cards provided by expansions
DODGE_CITY_COUNTS: List[Tuple[Type[Card], int]] = [
    (PunchCard, 4),
    (HideoutCard, 2),
    (BinocularsCard, 2),
    (BuffaloRifleCard, 1),
    (PepperboxCard, 1),
    (HowitzerCard, 1),
    (KnifeCard, 2),
    (BrawlCard, 2),
    (SpringfieldCard, 1),
    (SombreroCard, 1),
    (IronPlateCard, 1),
    (DerringerCard, 2),
    (BibleCard, 1),
    (CanteenCard, 1),
    (ConestogaCard, 1),
    (CanCanCard, 1),
    (TenGallonHatCard, 1),
]

FISTFUL_COUNTS: List[Tuple[Type[Card], int]] = [
    (WhiskyCard, 2),
    (TequilaCard, 3),
    (PonyExpressCard, 2),
    (RagTimeCard, 2),
]

HIGH_NOON_COUNTS: List[Tuple[Type[Card], int]] = [
    (HighNoonCard, 1),
]

EXPANSION_CARDS = {
    "dodge_city": DODGE_CITY_COUNTS,
    "fistful_of_cards": FISTFUL_COUNTS,
    "high_noon": HIGH_NOON_COUNTS,
}


def _generate_suits(count: int) -> List[str]:
    """Return a shuffled list of suits with nearly even distribution."""
    base = count // 4
    extra = count % 4
    suits_pool: List[str] = []
    for i, suit in enumerate(["Hearts", "Diamonds", "Clubs", "Spades"]):
        suits_pool.extend([suit] * (base + (1 if i < extra else 0)))
    random.shuffle(suits_pool)
    return suits_pool


def create_standard_deck(expansions: Iterable[str] | None = None) -> Deck:
    """Return a Deck built with cards using a balanced suit distribution.

    Parameters
    ----------
    expansions:
        Iterable of expansion names to include additional cards.
    """
    card_counts = CARD_COUNTS[:]
    if expansions:
        for exp in expansions:
            card_counts.extend(EXPANSION_CARDS.get(exp, []))

    total = sum(c for _, c in card_counts)
    suits = _generate_suits(total)
    ranks = list(range(1, 14)) * (total // 13 + 1)
    random.shuffle(ranks)

    cards: List[Card] = []
    idx = 0
    for card_cls, count in card_counts:
        for _ in range(count):
            suit = suits[idx % len(suits)]
            rank = ranks[idx % len(ranks)]
            cards.append(card_cls(suit=suit, rank=rank))
            idx += 1

    return Deck(cards)
