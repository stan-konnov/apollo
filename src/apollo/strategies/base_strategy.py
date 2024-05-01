from typing import Any, Type

from pandas import DataFrame

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.settings import NO_SIGNAL


class BaseStrategy:
    """
    Base class for all strategies.

    Defines basic interface to implement by child strategies.
    Contains the common attributes necessary for optimizing the strategy.
    """

    def __init__(self, dataframe: DataFrame, window_size: int) -> None:
        """
        Construct Base Strategy.

        Insert signal column.

        Calculate volatility for the strategy.

        All strategies are designed to be trailing strategies that
        apply dynamic limit, stop loss and take profit orders.

        The limit, stop loss and take profit levels are calculated based on:

        * Average True Range (ATR), which is a measure of volatility.
        * Volatility multiplier, which is a user-defined parameter.
        * Current closing price of the analyzed instrument.

        The job of calculating these levels is delegated to backtesting module,
        yet, the strategy is responsible for providing necessary inputs.
        Therefore, this method calculates volatility for all strategies.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        self.dataframe = dataframe
        self.window_size = window_size

        self.dataframe["signal"] = NO_SIGNAL

        self.atr_calculator = AverageTrueRangeCalculator(dataframe, window_size)
        self.atr_calculator.calculate_average_true_range()

    def model_trading_signals(self) -> None:
        """
        Model entry and exit signals.

        Is required to be implemented by subclasses.
        """

        raise NotImplementedError("Method model_trading_signals is not implemented")

    def _validate_parameters(self, parameters: list[tuple[str, Any, Type]]) -> None:
        """
        Validate that all parameters are provided and of type specified by the caller.

        Due to the fact that strategy specific parameters
        are different for each strategy, we do not have the
        way to properly type them in the BaseStrategy class.

        During optimization process, we read the parameters file
        and extract the specific parameters without knowing their types beforehand.

        Therefore, we resolve to spreading them as
        keyword arguments to the strategy constructor.

        Clearly, this is not the most elegant or type-safe solution.
        In such, every strategy is responsible for validating the parameters.

        :param parameters: Parameters to validate.
        :raises ValueError: If any parameter is missing.
        :raises TypeError: If any parameter is not of expected type.
        """

        for parameter in parameters:
            parameter_name, parameter_value, expected_type = parameter

            if parameter_value is None:
                raise ValueError(f"Parameter {parameter_name} is missing")

            if not isinstance(parameter_value, expected_type):
                raise TypeError(
                    f"Parameter {parameter_name} is "
                    f"not of expected type {expected_type.__name__}",
                )
