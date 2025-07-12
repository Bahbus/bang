from __future__ import annotations

from .barrel import BarrelCard


class SombreroCard(BarrelCard):
    """Protection equipment functioning like a Barrel from Dodge City."""

    card_name = "Sombrero"
    description = "Barrel-like protection; draw to avoid Bang!."
    green_border = True
