from pydantic import BaseModel


class SignalNotification(BaseModel):
    """
    A model to represent notification that signal was generated.

    Is used intra-system to communicate to the execution logic
    which position should be opened, updated, or closed on the market.
    """

    open_position: bool = False
    dispatched_position: bool = False
