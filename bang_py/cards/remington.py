from __future__ import annotations

from .equipment import EquipmentCard


class RemingtonCard(EquipmentCard):
    card_name = "Remington"
    slot = "Gun"
    range = 3
    description = "Gun with range 3."
