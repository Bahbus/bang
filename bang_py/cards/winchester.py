from __future__ import annotations

from .equipment import EquipmentCard


class WinchesterCard(EquipmentCard):
    card_name = "Winchester"
    slot = "Gun"
    range = 5
    description = "Gun with range 5."
