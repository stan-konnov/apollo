from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import DispatchedPositionAlreadyExistsError
from apollo.models.position import PositionStatus
from apollo.providers.price_data_provider import PriceDataProvider


class SignalDispatcher:
    """Signal Dispatcher class."""

    def __init__(self) -> None:
        """
        Construct Signal Dispatcher.

        TODO: handle existing open positions first.
        TODO: handle system invariants of managing filled, unfilled orders.

        Initialize Database Connector.
        Initialize Price Data Provider.
        """

        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()

    def dispatch_signals(self) -> None:
        """Generate and dispatch signals."""

        # Query existing dispatched position
        existing_dispatched_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.DISPATCHED,
            )
        )

        # Raise an error if the
        # dispatched position already exists
        if existing_dispatched_position:
            raise DispatchedPositionAlreadyExistsError(
                "Dispatched position for "
                f"{existing_dispatched_position.ticker} already exists. "
                "System invariant violated, position was not opened or cancelled.",
            )
