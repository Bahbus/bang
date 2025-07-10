from __future__ import annotations

from .equipment import EquipmentCard


class BuffaloRifleCard(EquipmentCard):
    """Long range gun from Dodge City."""

    card_name = "Buffalo Rifle"
    slot = "Gun"
    range = 5
    description = "Gun with range 5."
