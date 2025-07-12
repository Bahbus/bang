from __future__ import annotations

from .equipment import EquipmentCard


class PepperboxCard(EquipmentCard):
    """Gun from the Dodge City expansion with range 3."""

    card_name = "Pepperbox"
    slot = "Gun"
    range = 3
    description = "Gun with range 3."
    green_border = True
