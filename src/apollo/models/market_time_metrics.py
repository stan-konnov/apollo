from datetime import date, datetime

from pydantic import BaseModel


class MarketTimeMetrics(BaseModel):
    """
    A model to represent market time metrics.

    Used to determine different market timings
    in relation to signal generation and execution.
    """

    is_business_day: bool
    is_market_holiday: bool
    current_date_in_exchange: date
    open_datetime_in_exchange: datetime
    close_datetime_in_exchange: datetime
    current_datetime_in_exchange: datetime
