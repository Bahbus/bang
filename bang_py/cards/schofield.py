from __future__ import annotations

from .equipment import EquipmentCard


class SchofieldCard(EquipmentCard):
    card_name = "Schofield"
    slot = "Gun"
    range = 2
    description = "Gun with range 2."
