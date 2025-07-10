from __future__ import annotations

from .equipment import EquipmentCard


class BarrelCard(EquipmentCard):
    card_name = "Barrel"
    description = "Draw when targeted by Bang!; on Heart, ignore it."
