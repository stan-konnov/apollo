from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING, Any

import pandas_market_calendars as mcal
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest
from numpy import is_busday
from pandas import to_datetime
from zoneinfo import ZoneInfo

from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import (
    DispatchedPositionDoesNotExistError,
    OpenPositionAlreadyExistsError,
)
from apollo.models.position import PositionStatus
from apollo.settings import (
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    DEFAULT_TIME_FORMAT,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    LONG_SIGNAL,
)

if TYPE_CHECKING:
    from alpaca.trading.models import TradeAccount

logger = getLogger(__name__)


class MarketOrdersManager:
    """
    Market Orders Manager class.

    Exists as abstraction over Alpaca API, time and market calendar aware.
    """

    def __init__(self) -> None:
        """
        Construct Market Orders Manager.

        Initialize Trading Client.
        Initialize Account Client.
        Initialize Database Connector.
        """

        self._trading_client = TradingClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
        )

        self._account_client: TradeAccount | dict[str, Any] = (
            self._trading_client.get_account()
        )

        self._database_connector = PostgresConnector()

    def handle_dispatched_position(self) -> None:
        """
        Handle incoming dispatched position by placing an order.

        Communicate with Alpaca API to fetch the status
        of the order and synchronize it with the position in database.
        """

        # Query existing open position
        existing_open_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.OPEN,
            )
        )

        # Raise error if open position already exists
        if existing_open_position:
            raise OpenPositionAlreadyExistsError(
                "Open position exists while handling dispatched signal. "
                "System invariant violated, position was not closed or cancelled.",
            )

        # Query existing dispatched position
        existing_dispatched_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.DISPATCHED,
            )
        )

        # Raise error if no dispatched position exists
        if not existing_dispatched_position:
            raise DispatchedPositionDoesNotExistError(
                "Dispatched position does not exists while handling dispatched signal. "
                "System invariant violated, position was not dispatched.",
            )

        while True:
            # Determine if the execution can run
            if self._determine_if_can_run():
                # Determine limit price based on sub-penny
                # increment rules (no more than 2 decimal places)
                limit_price = round(
                    existing_dispatched_position.target_entry_price,  # type: ignore  # noqa: PGH003
                    2,
                )

                # Determine order quantity to execute based
                # on account balance and target entry price
                # NOTE: our account values are represented as strings,
                # so we convert to floats; target entry price is already a float
                order_quantity = int(
                    float(self._account_client.non_marginable_buying_power)  # type: ignore  # noqa: PGH003
                    / existing_dispatched_position.target_entry_price,
                )

                # Determine order side based
                # on the direction of the signal
                order_side = (
                    OrderSide.BUY
                    if existing_dispatched_position.direction == LONG_SIGNAL
                    else OrderSide.SELL
                )

                # Prepare limit order request
                limit_order_request = LimitOrderRequest(
                    symbol=existing_dispatched_position.ticker,
                    limit_price=limit_price,
                    qty=order_quantity,
                    side=order_side,
                    time_in_force=TimeInForce.IOC,
                )

                # And place an order
                limit_order = self._trading_client.submit_order(
                    order_data=limit_order_request,
                )

                logger.info(
                    f"Placed limit order for dispatched position: {limit_order} ",
                )

                # Break after placing an order
                # and synchronizing the position
                break

            logger.info(
                "Cannot execute at the moment. Waiting for the market to open.",
            )

    def _determine_if_can_run(self) -> bool:
        """Determine if the process can run based on time and market calendar."""

        # Get current point in time
        # in the configured exchange
        current_datetime_in_exchange = datetime.now(
            tz=ZoneInfo(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"],
            ),
        )

        # Current date in the exchange time zone
        current_date = current_datetime_in_exchange.date()

        # Get close point in time
        # in the configured exchange
        close_time_in_exchange = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
            DEFAULT_TIME_FORMAT,
        ).time()

        # Get open point in time
        # in the configured exchange
        open_time_in_exchange = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["open"],
            DEFAULT_TIME_FORMAT,
        ).time()

        # Get NYSE market holidays calendar
        market_holidays = mcal.get_calendar("NYSE").holidays().holidays  # type: ignore  # noqa: PGH003

        # Transform to regular python datetime objects
        market_holidays = [to_datetime(str(holiday)) for holiday in market_holidays]

        # And limit to dates of the current year
        market_holidays = [
            holiday.date()
            for holiday in market_holidays
            if holiday.year == current_datetime_in_exchange.year
        ]

        # Check if today is a business day in configured exchange
        is_business_day = bool(is_busday(current_date))

        # Check if today is market holiday in configured exchange
        is_market_holiday = current_date in market_holidays

        # Can run after market open,
        # but before close, on a business, non-holiday day
        return (
            is_business_day
            and not is_market_holiday
            and current_datetime_in_exchange.time() >= open_time_in_exchange
            and current_datetime_in_exchange.time() < close_time_in_exchange
        )
