from logging import getLogger
from time import sleep
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
from apollo.settings import (
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    LONG_SIGNAL,
)
from apollo.utils.market_time_aware import MarketTimeAware

if TYPE_CHECKING:
    from alpaca.trading.models import TradeAccount

logger = getLogger(__name__)


class OrderManager(MarketTimeAware):
    """
    Order Manager class.

    Time and market calendar aware.

    Exists as abstraction over Alpaca Trading API to manage market orders.
    """

    def __init__(self) -> None:
        """
        Construct Order Manager.

        Initialize Trading Client.
        Initialize Account Client.
        Initialize Database Connector.
        """

        super().__init__()

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

        logger.info("Handling dispatched position signal.")

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
            # Check if system can execute signals
            _, can_execute = self._determine_if_generate_or_execute()

            if can_execute:
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
                    # NOTE: experiment with DAY time in force
                    time_in_force=TimeInForce.IOC,
                )

                # And place an order
                limit_order = self._trading_client.submit_order(
                    order_data=limit_order_request,
                )

                logger.info(
                    f"Order for dispatched position:\n\n"
                    f"{limit_order.model_dump_json(indent=4)}",  # type: ignore  # noqa: PGH003
                )

                # Flag to control
                # synchronization of position
                position_synchronized = False

                # While the position is not synchronized
                while not position_synchronized:
                    # Query the position from the API
                    position_from_api = self._trading_client.get_open_position(
                        existing_dispatched_position.ticker,
                    )

                    # If position is still not opened
                    if not position_from_api:
                        logger.info(
                            "Position not opened, waiting for it to be created.",
                        )

                        # Yet, if market is about to close
                        if self._determine_if_market_is_closing():
                            logger.info(
                                "Market is about to close, "
                                "updating dispatched position status to CANCELLED.",
                            )

                            # Update dispatched position status to CANCELLED
                            self._database_connector.update_existing_position_by_status(
                                existing_dispatched_position.id,
                                PositionStatus.CANCELLED,
                            )

                            # And exit the loop
                            position_synchronized = True
                        else:
                            # Wait otherwise
                            sleep(5)
                            continue

                    # Otherwise,
                    # if position is opened
                    else:
                        logger.info(
                            "Position opened: "
                            "updating dispatched position status to OPEN.",
                        )

                        # Update dispatched position status to OPEN
                        self._database_connector.update_existing_position_by_status(
                            existing_dispatched_position.id,
                            PositionStatus.OPEN,
                        )

                        # And exit the loop
                        position_synchronized = True

                # Reset status logged flag
                self._status_logged = False

                # Break after placing an order
                # and synchronizing the position,
                # thus, returning the control flow
                # back to the generation execution runner
                break

            # Log status if not logged yet
            if not self._status_logged:
                self._status_logged = True

                logger.info(
                    "Cannot execute at the moment. Waiting for the market to open.",
                )
