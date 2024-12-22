from pydantic import BaseModel


class StrategyParameters(BaseModel):
    """
    A data model to represent strategy parameters.

    Exists to communicate strategy parameters
    to signal dispatching step after optimization.
    """

    strategy: str
    parameters: dict
