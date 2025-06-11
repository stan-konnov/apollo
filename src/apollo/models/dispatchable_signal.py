from pydantic import BaseModel


class PositionSignal(BaseModel):
    """
    A model to represent a signal for the position.

    Is used internally during signal generation process.
    """

    direction: int
    stop_loss: float
    take_profit: float
    target_entry_price: float


class DispatchableSignal(BaseModel):
    """
    A model to represent a dispatchable signal.

    Is used intra-system to communicate to the execution logic
    which position should be opened, updated, or closed on the market.
    """

    open_position: bool = False
    dispatched_position: bool = False
