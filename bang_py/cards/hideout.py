from __future__ import annotations

from .equipment import EquipmentCard


class HideoutCard(EquipmentCard):
    """Equipment increasing distance others see you by 1."""

    card_name = "Hideout"
    distance_modifier = 1
    description = "Opponents see you at +1 distance."

