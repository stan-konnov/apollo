from collections.abc import Iterable
from typing import TypedDict

from apollo.strategies.base.base_strategy import BaseStrategy


class ParameterSpec(TypedDict):
    """Parameter specification type definition."""

    name: str
    step: float
    range: list[float]


class ParameterSet(TypedDict):
    """Parameter set file type definition."""

    frequency: str
    cash_size: float

    window_size: ParameterSpec
    sl_volatility_multiplier: ParameterSpec
    tp_volatility_multiplier: ParameterSpec

    # Some strategies are enhanced
    # with additional data sources
    additional_data_enhancers: list[str]

    # Every strategy defines its own set of specific parameters
    # We do not know beforehand what these parameters are and cannot type them
    # They are still present as entries on parameters files
    # We use this list to index the specific parameters and pass them to the strategy
    strategy_specific_parameters: list[str]


ParameterCombinations = Iterable[tuple[float, ...]]
ParameterKeysAndCombinations = tuple[list[str], ParameterCombinations]


StrategyCatalogueMap = dict[str, type[BaseStrategy]]
