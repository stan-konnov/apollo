from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class PositionStatus(Enum):
    """An enumeration to represent the status of a position."""

    # Statuses relevant
    # to signal generation
    SCREENED = "screened"
    SUBMITTED = "submitted"
    DISPATCHED = "dispatched"

    # Statuses relevant
    # to market execution
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Position(BaseModel):
    """A data model to represent a position."""

    id: str

    ticker: str
    status: PositionStatus

    strategy: str
    direction: int
    limit_price: float

    entry_price: float
    entry_date: datetime
    unit_size: float
    cash_size: float

    stop_loss: float
    take_profit: float

    exit_price: float
    exit_date: datetime

    return_percent: float
    profit_and_loss: float
