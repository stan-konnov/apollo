from typing import Optional

import numpy as np
from pydantic import BaseModel, field_serializer


class PositionSignal(BaseModel):
    """A model to represent a signal for open or optimized position."""

    ticker: str
    position_id: str

    strategy: str
    direction: int
    stop_loss: float
    take_profit: float
    target_entry_price: float

    # Declare custom serializers
    # from numpy types to native Python types
    # as Pydantic does not support numpy types directly

    @field_serializer("direction")
    def serialize_direction(self, value: np.int64) -> int:
        """Convert numpy int64 to int for serialization."""
        return int(value)

    @field_serializer("stop_loss")
    def serialize_stop_loss(self, value: np.float64) -> float:
        """Convert numpy float64 to float for serialization."""
        return float(value)

    @field_serializer("take_profit")
    def serialize_take_profit(self, value: np.float64) -> float:
        """Convert numpy float64 to float for serialization."""

        return float(value)

    @field_serializer("target_entry_price")
    def serialize_target_entry_price(self, value: np.float64) -> float:
        """Convert numpy float64 to float for serialization."""
        return float(value)


class Signal(BaseModel):
    """A model to represent a signal for dispatching."""

    open_position: Optional[PositionSignal] = None
    dispatched_position: Optional[PositionSignal] = None
