from typing import ClassVar, Optional

import numpy as np
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

    class Config:
        """Configuration for converting numpy types to natives."""

        json_encoders: ClassVar = {
            np.float64: float,
            np.int64: int,
        }


class Signal(BaseModel):
    """A model to represent a signal for dispatching."""

    open_position: Optional[PositionSignal] = None
    dispatched_position: Optional[PositionSignal] = None
