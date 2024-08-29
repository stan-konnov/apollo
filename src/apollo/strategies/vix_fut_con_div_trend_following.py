from pandas import DataFrame

from apollo.calculations.vix_futures_convergence_divergence import (
    VixFutureConvergenceDivergenceCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)

"""
TODO: this should be renamed, calculator should incapsulate

Enhancing strategy should be created

FROM EXPERIMENTS:

Working version is TREND FOLLOWING
"""

"""
Trend following:

LONG:

- Instrument is increasing
- VIX is decreasing
- S&P 500 Futures is increasing

SHORT:

- Instrument is decreasing
- VIX is increasing
- S&P 500 Futures is decreasing

Daily Percentage Difference and What It Tells You
If you're looking at the daily percentage change of both
the VIX and S&P 500 futures and then subtracting the S&P 500's
daily percentage change from the VIX's, here's what it generally means:

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

Key Takeaways:

Positive differences often indicate heightened
fear or caution relative to the market movement.

Negative differences suggest market confidence, but the
degree of VIX movement relative to S&P 500
can reveal how much caution or hedging is present.

DIVERGENCE = POSITIVE RESULT:

This occurs when the VIX daily percentage change is
greater than the S&P 500 futures daily
percentage change (i.e., the VIX is rising more than the S&P 500 is falling,
or it's falling less than the S&P 500 is rising).
This indicates a divergence in market sentiment,
with higher levels of fear or caution relative to the actual market movement.

CONVERGENCE = NEGATIVE RESULT:

This occurs when the S&P 500 futures
daily percentage change is greater than the VIX daily percentage change
(i.e., the S&P 500 is rising more than the VIX is falling,
or it's falling less than the VIX is rising).
This indicates a convergence in market sentiment,
where the market movement and volatility expectations are more aligned.

Increasing Difference (Divergence Growing):
Indicates rising fear or volatility expectations relative to market movements.

Decreasing Difference (Convergence Growing):
Indicates stabilizing market sentiment with
volatility expectations more closely tracking market movements.
"""


class VIXFuturesConvergenceDivergenceTrendFollowing(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Work in progress.

    Massive work in progress:
    we might not even use Dunnigan, experimenting.
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

        self._vfcd_calculator = VixFutureConvergenceDivergenceCalculator(
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
