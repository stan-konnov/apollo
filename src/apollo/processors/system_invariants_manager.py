from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import (
    OptimizedPositionAlreadyExistsError,
    ScreenedPositionAlreadyExistsError,
)


class SystemInvariantsManager:
    """
    System Invariants Manager class.

    Responsible for validating the health of position lifecycle.
    Is used in between and within system steps to ensure the following rules:

    1. No screened position exists before the screening process.
    3. No optimized position exists before the optimization process.
    3. No active position for a given ticker exists after the screening process.

    "It never hurts to double-check."
    """

    def __init__(self) -> None:
        """
        Construct System Invariants Manager.

        Initialize Database Connector.
        """

        self._database_connector = PostgresConnector()

    def validate_no_screened_position_exists_before_screening(self) -> None:
        """
        Validate that no screened position exists before the screening process.

        Raise ScreenedPositionAlreadyExistsError if screened position exists.
        """

        # Query existing screened position
        existing_screened_position = (
            self._database_connector.get_existing_screened_position()
        )

        # And raise error if exists
        if existing_screened_position:
            raise ScreenedPositionAlreadyExistsError(
                "Screened position for ",
                f"{existing_screened_position.ticker} already exists. "
                "System invariant violated, previous position not dispatched.",
            )

    def validate_no_optimized_position_exists_before_optimization(self) -> None:
        """
        Validate that no optimized position exists before the optimization process.

        Raise OptimizedPositionAlreadyExistsError if optimized position exists.
        """

        # Query existing optimized position
        existing_optimized_position = (
            self._database_connector.get_existing_optimized_position()
        )

        # And raise error if exists
        if existing_optimized_position:
            raise OptimizedPositionAlreadyExistsError(
                "Optimized position for ",
                f"{existing_optimized_position.ticker} already exists. "
                "System invariant violated, previous position not dispatched.",
            )
