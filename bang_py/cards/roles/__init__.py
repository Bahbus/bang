"""Role card exports defining player objectives."""

from .base import BaseRole
from .sheriff import SheriffRoleCard
from .deputy import DeputyRoleCard
from .outlaw import OutlawRoleCard
from .renegade import RenegadeRoleCard

__all__ = [
    "BaseRole",
    "SheriffRoleCard",
    "DeputyRoleCard",
    "OutlawRoleCard",
    "RenegadeRoleCard",
]
