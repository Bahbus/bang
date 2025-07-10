from __future__ import annotations

from .equipment import EquipmentCard


class VolcanicCard(EquipmentCard):
    card_name = "Volcanic"
    slot = "Gun"
    range = 1
    description = "Gun with range 1."
