from __future__ import annotations

from .equipment import EquipmentCard


class MustangCard(EquipmentCard):
    card_name = "Mustang"
    distance_modifier = 1
    description = "Opponents see you at 1 greater distance."
