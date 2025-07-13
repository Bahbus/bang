from __future__ import annotations

from .equipment import EquipmentCard


class BinocularsCard(EquipmentCard):
    """Equipment increasing your attack range by 1."""

    card_name = "Binoculars"
    range_modifier = 1
    description = "Increases attack range by 1."

