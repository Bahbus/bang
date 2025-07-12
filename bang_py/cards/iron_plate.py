from __future__ import annotations

from .equipment import EquipmentCard


class IronPlateCard(EquipmentCard):
    """Equipment that increases your maximum health by 1."""

    card_name = "Iron Plate"
    description = "Equipment: +1 maximum health."
    max_health_modifier = 1
    green_border = True
