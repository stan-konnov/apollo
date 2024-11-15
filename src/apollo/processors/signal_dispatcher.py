from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.providers.price_data_provider import PriceDataProvider


class SignalDispatcher:
    """Signal Dispatcher class."""

    def __init__(self) -> None:
        """
        Construct Signal Dispatcher.

        Initialize Database Connector.
        Initialize Price Data Provider.
        """

        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()

    def dispatch_signals(self) -> None:
        """Generate and dispatch signals."""

        # First and foremost, we have to
        # check if we already have an open position
        _existing_open_position = self._database_connector.get_existing_open_position()

        # If we do, generate TP and SL brackets
