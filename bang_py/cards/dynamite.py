from __future__ import annotations

from .equipment import EquipmentCard


class DynamiteCard(EquipmentCard):
    card_name = "Dynamite"
    description = "Passes around; may explode for 3 damage."
