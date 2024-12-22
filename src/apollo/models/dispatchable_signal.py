from typing import Optional

from pydantic import BaseModel


class PositionSignal(BaseModel):
    """A model to represent a signal for open or optimized position."""

    ticker: str
    position_id: str

    strategy: str
    direction: int
    stop_loss: float
    take_profit: float
    target_entry_price: float


class DispatchableSignal(BaseModel):
    """A model to represent a signal for dispatching."""

    open_position: Optional[PositionSignal] = None
    optimized_position: Optional[PositionSignal] = None
