from logging import getLogger
from typing import TYPE_CHECKING, Any

from alpaca.trading.client import TradingClient

from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.settings import (
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
)
from apollo.utils.log_controllable import LogControllable
from apollo.utils.market_time_aware import MarketTimeAware

if TYPE_CHECKING:
    from alpaca.trading.models import TradeAccount

logger = getLogger(__name__)


class BaseOrderManager(MarketTimeAware, LogControllable):
    """
    Base Order Manager class.

    Time and market calendar aware.

    Exists as a base for other order managers to manage market orders.
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
