"""Turn phase mixins grouped into a package."""

from .draw_phase import DrawPhaseMixin
from .discard_phase import DiscardPhaseMixin
from .turn_flow import TurnFlowMixin


class TurnPhasesMixin(DrawPhaseMixin, DiscardPhaseMixin, TurnFlowMixin):
    """Combine draw, discard and turn flow behaviors."""

    pass


__all__ = [
    "TurnPhasesMixin",
    "DrawPhaseMixin",
    "DiscardPhaseMixin",
    "TurnFlowMixin",
]
