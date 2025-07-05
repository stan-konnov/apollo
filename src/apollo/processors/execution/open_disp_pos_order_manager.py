from apollo.processors.execution.base_order_manager import BaseOrderManager


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
