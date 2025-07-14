from __future__ import annotations

from .equipment import EquipmentCard


class RevCarabineCard(EquipmentCard):
    """Classic gun with range 4."""

    card_name = "Rev. Carabine"
    slot = "Gun"
    range = 4
    description = "Gun with range 4."
