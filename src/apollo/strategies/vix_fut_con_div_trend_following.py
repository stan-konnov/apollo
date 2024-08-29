from pandas import DataFrame

from apollo.calculations.vix_futures_convergence_divergence import (
    VixFuturesConvergenceDivergenceCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)

"""
NEGATIVE RESULT (SP500 CHANGE > VIX CHANGE):

Convergence Growing

Scenario A: S&P 500 rises more than the VIX falls.
Interpretation: The market is in a risk-on mode, meaning investors are feeling confident
and theres a strong upward movement in the S&P 500.
The VIX falling less in comparison might indicate that while theres confidence,
theres still some underlying caution about potential risks.

Scenario B: Both VIX and S&P 500 are rising, but the S&P 500 rises more.
Interpretation: This could indicate a somewhat unusual
market condition where the market is bullish,
but theres still significant hedging activity or concerns about future volatility,
causing the VIX to rise even though the S&P 500 is also rising.

POSITIVE RESULT (VIX CHANGE > SP500 CHANGE):

Divergence Growing

Scenario A: VIX rises more than the S&P 500 falls
(or VIX falls less than S&P 500 rises).

Interpretation: The market is experiencing higher-than-usual fear or uncertainty.
If the VIX rises sharply while the S&P 500 falls,
it indicates that the market is anticipating increased volatility.
This can occur during market corrections,
economic uncertainty, or when significant news impacts investor sentiment.

Scenario B: Both VIX and S&P 500 futures are falling, but the VIX falls less.

Interpretation: This could suggest that although the market is calm
(hence the VIX is falling),
theres still a degree of caution or hedging going on.
The S&P 500 might be falling,
but the VIXs lesser drop indicates that traders arent fully confident
that the market's decline will continue without increased volatility.
"""


class VIXFuturesConvergenceDivergenceTrendFollowing(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    VIX Futures Convergence Divergence Trend Following Strategy.

    This strategy takes long positions when:

    * Instrument close price is increasing, indicating a potential uptrend.

    * VIX on Futures percentage difference is decreasing,
    indicating a convergence in market sentiment.

    This strategy takes short positions when:

    * Instrument close price is decreasing, indicating a potential downtrend.

    * VIX on Futures percentage difference is increasing,
    indicating a divergence in market sentiment.

    Decreasing difference (convergence growing) captures two bullish scenarios:

    * S&P 500 rises more than the VIX falls -- a sign of market confidence
    and a strong (accompanied by volatility) upward movement in the S&P 500.

    * Both VIX and S&P 500 are rising, but the S&P 500 rises more -- a sign of a still
    bullish market accompanied by hedging activity or concerns about future volatility.

    Convergence is, therefore, used to confirm a potential uptrend.

    Increasing difference (divergence growing) captures two bearish scenarios:

    * VIX rises more than the S&P 500 falls -- a sign of higher-than-usual
    anticipation of increased volatility, occurring during market corrections.

    * Both VIX and S&P 500 futures are falling, but the VIX falls less -- a sign of
    of bearish market accompanied by concerns about further growing volatility.

    Divergence is, therefore, used to confirm a potential downtrend.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Work in progress.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._vfcd_calculator = VixFuturesConvergenceDivergenceCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._vfcd_calculator.calculate_vix_futures_convergence_divergence()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (self._dataframe["adj close"] > self._dataframe["prev_close"]) & (
            self._dataframe["vix_spf_pct_diff"]
            < self._dataframe["prev_vix_spf_pct_diff"]
        )

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self._dataframe["adj close"] < self._dataframe["prev_close"]) & (
            self._dataframe["vix_spf_pct_diff"]
            > self._dataframe["prev_vix_spf_pct_diff"]
        )

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
