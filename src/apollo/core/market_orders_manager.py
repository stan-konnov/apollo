from typing import TYPE_CHECKING, Any

from alpaca.trading.client import TradingClient

from apollo.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY

if TYPE_CHECKING:
    from alpaca.trading.models import TradeAccount


class MarketOrdersManager:
    """
    Market Orders Manager class.

    Exists as abstraction over Alpaca API, time and market calendar aware.
    """

    def __init__(self) -> None:
        """Construct Market Orders Manager."""

        # Initialize trading client
        self._trading_client = TradingClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
        )

        # Fetch account information
        self._account: TradeAccount | dict[str, Any] = (
            self._trading_client.get_account()
        )

    def handle_dispatched_position(self) -> None:
        """
        Handle incoming dispatched position by placing an order.

        :param dispatched_position: Dispatched position to handle.
        """
