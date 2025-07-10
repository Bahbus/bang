from __future__ import annotations

from .equipment import EquipmentCard


class CarbineCard(EquipmentCard):
    card_name = "Carbine"
    slot = "Gun"
    range = 4
    description = "Gun with range 4."
