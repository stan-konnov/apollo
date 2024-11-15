from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.models.position import PositionStatus
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
        """
        Generate and dispatch signals.

        Handle system invariants related to dispatching step.
        """

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

        # Query existing open position
        existing_open_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.OPEN,
            )
        )

        # Query existing optimized position
        existing_optimized_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.OPTIMIZED,
            )
        )

        # Raise an error if neither
        # open nor optimized position exists
        if not existing_open_position and not existing_optimized_position:
            raise NeitherOpenNorOptimizedPositionExistsError(
                "Neither open nor optimized position exists. "
                "System invariant violated, position was not opened or optimized.",
            )
