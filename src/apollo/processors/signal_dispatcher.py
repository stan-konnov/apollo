from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.providers.price_data_provider import PriceDataProvider


class SignalDispatcher:
    """Signal Dispatcher class."""

    def __init__(self) -> None:
        """
        Construct Signal Dispatcher.

        TODO: handle existing open positions first.
        TODO: simplify database connector to and write position by status.

        Initialize Database Connector.
        Initialize Price Data Provider.
        """

        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()

    def dispatch_signals(self) -> None:
        """Generate and dispatch signals."""

        # Query optimized position
        _existing_optimized_position = (
            self._database_connector.get_existing_optimized_position()
        )

        # Query existing dispatched position
        _existing_dispatched_position = (
            self._database_connector.get_existing_dispatched_position()
        )
