from __future__ import annotations

from .equipment import EquipmentCard


class VolcanicCard(EquipmentCard):
    card_name = "Volcanic"
    slot = "Gun"
    range = 1
    # Allows the player to fire unlimited Bang! cards during their turn
    unlimited_bang = True
    description = "Gun with range 1. Allows unlimited Bang! cards per turn."
