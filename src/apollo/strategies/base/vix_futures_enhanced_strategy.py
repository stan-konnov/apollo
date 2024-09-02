import pandas as pd

from apollo.calculations.vix_futures_convergence_divergence import (
    VixFuturesConvergenceDivergenceCalculator,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL

"""
TODO:

1. Precalculate prev_close and remove it from individual calculators.
   (Done, double check).

2. On missing data = we need to drop since we need valid ATR to calculate
    entries and exits.

3. Every enhanced strategy or strategy that relies on enhanced data
   should validate if the data is present in the dataframe before using it.

4. Go through every strategy top to bottom and figure out if they
   can be enhanced with VIX Futures signals.

5. Use futures high and low for enhancing instead of VIX Futures Conv Divergence.
"""


class VIXFuturesEnhancedStrategy:
    """
    VIX Futures Enhanced Strategy class.

    Uses VIX index and S&P500 prices to enhance signal
    generation logic of specialized strategies.

    Calculates VIX Futures Convergence
    Divergence and generates VIX Futures enhanced signal.

    This strategy takes long positions when:

    * Instrument close price is increasing,
    indicating a potential uptrend.

    * VIX on Futures percentage difference is decreasing,
    indicating a convergence in market sentiment.

    This strategy takes short positions when:

    * Instrument close price is decreasing,
    indicating a potential downtrend.

    * VIX on Futures percentage difference is increasing,
    indicating a divergence in market sentiment.

    Decreasing difference (convergence growing) captures two bullish scenarios:

    * S&P 500 rises more than the VIX falls -- a sign of market confidence
    and a strong (accompanied by volatility) upward movement in the S&P 500.

    * Both VIX and S&P 500 are rising, but the S&P 500 rises more -- a sign of
    a still bullish market accompanied by concerns about future volatility.

    Convergence is, therefore, used to confirm a potential uptrend.

    Increasing difference (divergence growing) captures two bearish scenarios:

    * VIX rises more than the S&P 500 falls -- a sign of higher-than-usual
    anticipation of increased volatility, occurring during market corrections.

    * Both VIX and S&P 500 futures are falling, but the VIX falls less -- a sign of
    of bearish market accompanied by concerns about even further growing volatility.

    Divergence is, therefore, used to confirm a potential downtrend.

    NOTE: This strategy class is not a standalone strategy
    and should be used in conjunction with other strategies.

    Yet, the logic of VIX Futures signals proved to be effective
    enough and, therefore, is applied in isolation in
    VIX Futures Convergence Divergence Trend Following class.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct VIX Futures Enhanced Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        # Calculate VIX Futures Convergence Divergence
        self._vfcd_calculator = VixFuturesConvergenceDivergenceCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )
        self._vfcd_calculator.calculate_vix_futures_convergence_divergence()

        # Mark VIX Futures enhanced signals to the dataframe
        dataframe["vix_spf_signal"] = NO_SIGNAL

        long = (dataframe["adj close"] > dataframe["prev_close"]) & (
            dataframe["vix_spf_pct_diff"] < dataframe["prev_vix_spf_pct_diff"]
        )

        dataframe.loc[long, "vix_spf_signal"] = LONG_SIGNAL

        short = (dataframe["adj close"] < dataframe["prev_close"]) & (
            dataframe["vix_spf_pct_diff"] > dataframe["prev_vix_spf_pct_diff"]
        )

        dataframe.loc[short, "vix_spf_signal"] = SHORT_SIGNAL
