from typing import Any

from pandas import DataFrame

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
        Precalculate shared values.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        self._dataframe = dataframe
        self._window_size = window_size

        self._precalculate_shared_values()
        self._dataframe["signal"] = NO_SIGNAL

    def model_trading_signals(self) -> None:
        """
        Model entry and exit signals.

        Is required to be implemented by subclasses.
        """

        raise NotImplementedError("Method model_trading_signals is not implemented.")

    def _validate_parameters(self, parameters: list[tuple[str, Any, type]]) -> None:
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

    def _precalculate_shared_values(self) -> None:
        """Precalculate values used in multiple strategies."""

        # Precalculate previous close
        self._dataframe["prev_close"] = self._dataframe["adj close"].shift(1)
