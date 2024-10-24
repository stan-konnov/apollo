import numpy as np
import pandas as pd
from scipy.stats import linregress

from apollo.calculations.base.base_calculator import BaseCalculator


class LinearRegressionChannelCalculator(BaseCalculator):
    """
    Linear Regression Channel Calculator.

    Uses rolling ordinary least squares regression.
    Channel bounds are expressed as +/- N standard deviations from the line of best fit.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Construct Linear Regression Channel Calculator.

        :param dataframe: Dataframe to calculate channel for.
        :param window_size: Window size for rolling channel calculation.
        :param channel_sd_spread: Standard deviation spread for channel bounds.
        """

        super().__init__(dataframe, window_size)

        self._t_slope: list[float] = []
        self._l_bound: list[float] = []
        self._u_bound: list[float] = []

        self._channel_sd_spread = channel_sd_spread

    def calculate_linear_regression_channel(self) -> None:
        """Calculate rolling linear regression channel."""

        # Reset indices to integer to use as x axis of linear regression
        self._dataframe.reset_index(inplace=True)

        # Fill slopes and bounds arrays with N NaN, where N = window size
        self._t_slope = np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        self._l_bound = np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        self._u_bound = np.full((1, self._window_size - 1), np.nan).flatten().tolist()

        # Calculate bounds and slope by using ordinary least squares regression
        self._dataframe["adj close"].rolling(self._window_size).apply(
            self._calc_lin_reg,
        )

        # Write slopes to dataframe
        self._dataframe["slope"] = self._t_slope

        # Shift slopes to further compare direction
        self._dataframe["prev_slope"] = self._dataframe["slope"].shift(1)

        # Write bounds to the dataframe
        self._dataframe["l_bound"] = self._l_bound
        self._dataframe["u_bound"] = self._u_bound

        # Reset indices back to date
        self._dataframe.set_index("date", inplace=True)

    def _calc_lin_reg(self, series: pd.Series) -> float:
        """
        Calculate rolling ordinary least squares regression for a given window.

        :param series: Series to calculate rolling linear regression over.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Use indices for x axis
        x = series.index

        # Use closing prices for y axis
        y = series.to_numpy()

        # Calculate slope and intercept, ignore rest
        slope, intercept, _, _, _ = linregress(x, y)

        # Preserve slope
        self._t_slope.append(slope)  # type: ignore  # noqa: PGH003

        # Calculate line of best fit
        lbf = slope * x + intercept

        # Calculate standard deviation
        std = y.std()

        # Calculate lower and upper bounds
        # as N standard deviations above/below LBF
        lower_bound = lbf - std * self._channel_sd_spread
        upper_bound = lbf + std * self._channel_sd_spread

        self._l_bound.append(lower_bound[-1])
        self._u_bound.append(upper_bound[-1])

        # Return dummy float
        return 0.0
