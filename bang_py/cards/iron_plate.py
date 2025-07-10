from __future__ import annotations

from .equipment import EquipmentCard


class IronPlateCard(EquipmentCard):
    """Equipment that increases your maximum health by 1."""

    card_name = "Iron Plate"
    max_health_modifier = 1
