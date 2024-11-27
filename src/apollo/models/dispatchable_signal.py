from typing import Optional

from pydantic import BaseModel

from apollo.models.position import PositionStatus


class PositionSignal(BaseModel):
    """A model to represent a signal for open or optimized position."""

    ticker: str
    position_id: str
    position_status: PositionStatus

    direction: Optional[int] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    target_entry_price: Optional[float] = None


class DispatchableSignal(BaseModel):
    """A model to represent a signal for dispatching."""

    open_position: Optional[PositionSignal] = None
    optimized_position: Optional[PositionSignal] = None
