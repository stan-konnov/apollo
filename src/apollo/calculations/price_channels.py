import numpy as np
import pandas as pd
from scipy.stats import linregress

from apollo.calculations.base_calculator import BaseCalculator

# TODO: please rename me to OrdinaryLeastSquaresChannelCalculator


class PriceChannelsCalculator(BaseCalculator):
    """
    Price Channels calculator.

    Uses rolling linear regression.
    Preserves slope and previous slope.
    Channel bounds are expressed as +/- N
    standard deviations from the line of best fit.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Construct Price Channels calculator.

        :param dataframe: Dataframe to calculate price channels for.
        :param window_size: Window size for rolling price channels calculation.
        :param channel_sd_spread: Standard deviation spread for channel bounds.
        """

        super().__init__(dataframe, window_size)

        self.t_slope: list[float] = []
        self.l_bound: list[float] = []
        self.u_bound: list[float] = []
        self.bf_line: list[float] = []

        self.t_plus_n_price: list[float] = []
        self.f_plus_n_price: list[float] = []

        self.channel_sd_spread = channel_sd_spread


    def calculate_price_channels(self) -> None:
        """Calculate rolling price channels."""

        # Reset indices to integer to use as x axis of linear regression
        self.dataframe.reset_index(inplace=True)

        # Fill slopes, bounds and lbf arrays with N NaN, where N = window size
        self.t_slope = np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        self.l_bound = np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        self.u_bound = np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        self.bf_line = np.full((1, self.window_size - 1), np.nan).flatten().tolist()

        self.t_plus_n_price = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )
        self.f_plus_n_price = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate bounds and slope by using linear regression
        self.dataframe["adj close"].rolling(self.window_size).apply(
            self.__calc_lin_reg,
        )

        # Write slopes to dataframe
        self.dataframe["slope"] = self.t_slope

        # Shift slopes to further compare direction
        self.dataframe["prev_slope"] = self.dataframe["slope"].shift(1)

        # Write bounds to the dataframe
        self.dataframe["l_bound"] = self.l_bound
        self.dataframe["u_bound"] = self.u_bound

        # Write line of best fit to the dataframe
        self.dataframe["lbf"] = self.bf_line

        # Write projected price for t + window_size to the dataframe
        self.dataframe["t_plus_n_price"] = self.t_plus_n_price

        # Write forecasted price for t + window_size to the dataframe
        self.dataframe["f_plus_n_price"] = self.f_plus_n_price

        # Reset indices back to date
        self.dataframe.set_index("date", inplace=True)


    def __calc_lin_reg(self, series: pd.Series) -> float:
        """
        Calculate rolling linear regression for a given window.

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
        self.t_slope.append(slope)

        # Calculate line of best fit
        lbf: pd.Series = slope * x + intercept

        # Project price for t + window_size
        projection = y + self.window_size * slope

        # Preserve projected price
        self.t_plus_n_price.append(projection[-1])

        # Calculate residual
        residual = y - lbf

        # Forecast the price based on residual
        forecast = projection + self.channel_sd_spread * residual

        # Preserve forecast
        self.f_plus_n_price.append(forecast[-1])

        # Preserve LBF
        self.bf_line.append(lbf[-1])

        # Calculate standard deviation
        std = y.std()

        # Calculate lower and upper bounds
        # as N standard deviations above/below LBF
        lower_bound = lbf - std * self.channel_sd_spread
        upper_bound = lbf + std * self.channel_sd_spread

        self.l_bound.append(lower_bound[-1])
        self.u_bound.append(upper_bound[-1])

        # Return dummy float
        return 0.0
