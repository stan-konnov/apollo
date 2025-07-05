from logging import getLogger

from apollo.errors.system_invariants import (
    DispatchedPositionDoesNotExistError,
    OpenPositionDoesNotExistError,
)
from apollo.models.position import PositionStatus
from apollo.processors.execution.base_order_manager import BaseOrderManager

logger = getLogger(__name__)


class OpenDispatchedPositionOrderManager(BaseOrderManager):
    """
    Open Dispatched Position Order Manager class.

    Manages open and dispatched positions by placing
    orders and synchronizing them with position in the database.
    """

    def __init__(self) -> None:
        """Construct Open Dispatched Position Order Manager."""

        super().__init__()

    def handle_open_dispatched_position(self) -> None:
        """
        Handle incoming open and dispatched positions by placing orders.

        Communicate with Alpaca API to fetch the status
        of the orders and synchronize them with positions in the database.
        """

        logger.info("Handling open-dispatched position signal.")

        # Query existing open position
        existing_open_position = self._database_connector.get_position_by_status(
            PositionStatus.OPEN,
        )

        # Raise error if no open position exists
        if not existing_open_position:
            raise OpenPositionDoesNotExistError(
                "Open position does not exist while handling OD signal. "
                "System invariant violated, position was not opened.",
            )

        # Query existing dispatched position
        existing_dispatched_position = self._database_connector.get_position_by_status(
            PositionStatus.DISPATCHED,
        )

        # Raise error if no dispatched position exists
        if not existing_dispatched_position:
            raise DispatchedPositionDoesNotExistError(
                "Dispatched position does not exist while handling OD signal. "
                "System invariant violated, position was not dispatched.",
            )
