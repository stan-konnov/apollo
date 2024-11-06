from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PositionStatus(str, Enum):
    """An enum to represent the status of a position."""

    # Statuses relevant
    # to market execution
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

    # Statuses relevant
    # to signal generation
    SCREENED = "screened"
    OPTIMIZED = "optimized"
    DISPATCHED = "dispatched"


class Position(BaseModel):
    """
    A data model to represent a position.

    Please see /prisma/schema.prisma for
    detailed explanation of nullable fields.
    """

    ticker: str
    status: PositionStatus

    strategy: Optional[str] = None
    direction: Optional[int] = None
    target_entry_price: Optional[float] = None

    entry_price: Optional[float] = None
    entry_date: Optional[datetime] = None
    unit_size: Optional[float] = None
    cash_size: Optional[float] = None

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None

    return_percent: Optional[float] = None
    profit_and_loss: Optional[float] = None
