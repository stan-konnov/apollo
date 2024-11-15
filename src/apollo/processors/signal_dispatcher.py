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
