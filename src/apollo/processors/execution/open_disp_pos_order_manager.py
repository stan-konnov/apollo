from apollo.processors.execution.base_order_manager import BaseOrderManager


class OpenDispatchedPositionOrderManager(BaseOrderManager):
    """
    Open Dispatched Position Order Manager class.

    Manages open and dispatched positions by placing
    orders and synchronizing them with position in database.
    """

    def __init__(self) -> None:
        """Construct Open Dispatched Position Order Manager."""

        super().__init__()
