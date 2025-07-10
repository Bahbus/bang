from __future__ import annotations

from .equipment import EquipmentCard


class DerringerCard(EquipmentCard):
    """Short range gun from Dodge City."""

    card_name = "Derringer"
    slot = "Gun"
    range = 1
    description = "Gun with range 1."
