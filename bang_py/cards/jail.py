from __future__ import annotations

from .equipment import EquipmentCard


class JailCard(EquipmentCard):
    card_name = "Jail"
    description = "Skip your turn unless you draw a Heart."
