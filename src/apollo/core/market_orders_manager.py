from logging import getLogger
from typing import TYPE_CHECKING, Any

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest

from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import (
    DispatchedPositionDoesNotExistError,
    OpenPositionAlreadyExistsError,
)
from apollo.models.position import PositionStatus
from apollo.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, LONG_SIGNAL

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
        """Handle incoming dispatched position by placing an order."""

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

        # Determine limit price based on sub-penny
        # increment rules (no more than 2 decimal places)
        limit_price = round(
            existing_dispatched_position.target_entry_price,  # type: ignore  # noqa: PGH003
            2,
        )

        # Determine the notional amount to execute
        # based on account balance and target entry price
        # NOTE: our account values are represented as strings,
        # so we need to convert to floats; whereas target entry price is already a float
        notional_amount = int(
            float(self._account_client.cash)  # type: ignore  # noqa: PGH003
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
            notional=notional_amount,
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
