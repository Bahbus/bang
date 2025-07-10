from __future__ import annotations

from .equipment import EquipmentCard


class ScopeCard(EquipmentCard):
    card_name = "Scope"
    range_modifier = 1
    description = "Increases your attack range by 1."
