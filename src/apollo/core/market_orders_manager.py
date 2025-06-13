from logging import getLogger
from typing import TYPE_CHECKING, Any

from alpaca.trading.client import TradingClient

from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import OpenPositionAlreadyExistsError
from apollo.models.position import PositionStatus
from apollo.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY

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

        :param dispatched_position: Dispatched position to handle.
        """

        # First, check if there is no open
        # position to maintain system consistency
        existing_open_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.OPEN,
            )
        )

        if existing_open_position:
            raise OpenPositionAlreadyExistsError(
                "Open position exists while handling dispatched. "
                "System invariant violated, position was not closed or cancelled.",
            )
