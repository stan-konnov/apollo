from numpy import long
from pandas import DataFrame

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)

# ruff: noqa

"""
TODO: this should be renamed, calculator should incapsulate

Enhancing strategy should be created

FROM EXPERIMENTS:

Working version is TREND FOLLOWING
"""


class DunniganTrendFollowing(
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

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        # NOTE: if this works, move it to calculations

        # Sharpe: 1.53

        # self._dataframe["prev_vix_close"] = self._dataframe["vix close"].shift(1)
        # self._dataframe["prev_spf_close"] = self._dataframe["spf close"].shift(1)

        # long = (self._dataframe["vix close"] < self._dataframe["prev_vix_close"]) & (
        #     self._dataframe["spf close"] > self._dataframe["prev_spf_close"]
        # )

        # short = (self._dataframe["vix close"] > self._dataframe["prev_vix_close"]) & (
        #     self._dataframe["spf close"] < self._dataframe["prev_spf_close"]
        # )

        ####

        # Sharpe: 1.94

        # self._dataframe["pct_change"] = self._dataframe["adj close"].pct_change()

        # self._dataframe["vix_pct_change"] = self._dataframe["vix close"].pct_change()
        # self._dataframe["spf_pct_change"] = self._dataframe["spf close"].pct_change()

        # self._dataframe["vix_spf_pct_change_diff"] = (
        #     self._dataframe["vix_pct_change"] - self._dataframe["spf_pct_change"]
        # )

        # long = (
        #     self._dataframe["vix_spf_pct_change_diff"] > self._dataframe["pct_change"]
        # )
        # short = (
        #     self._dataframe["vix_spf_pct_change_diff"] < self._dataframe["pct_change"]
        # )

        ####

        # Sharpe: 2.18

        # self._dataframe["pct_change"] = self._dataframe["adj close"].pct_change()

        # self._dataframe["vix_pct_change"] = self._dataframe["vix close"].pct_change()
        # self._dataframe["spf_pct_change"] = self._dataframe["spf close"].pct_change()

        # self._dataframe["vix_spf_pct_change_diff"] = (
        #     self._dataframe["vix_pct_change"] - self._dataframe["spf_pct_change"]
        # )

        # self._dataframe["pct_change_diff"] = (
        #     self._dataframe["pct_change"] - self._dataframe["vix_spf_pct_change_diff"]
        # )

        # self._dataframe["prev_pct_change_diff"] = self._dataframe[
        #     "pct_change_diff"
        # ].shift(1)

        # long = (
        #     self._dataframe["pct_change_diff"] > self._dataframe["prev_pct_change_diff"]
        # )

        # self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        # short = (
        #     self._dataframe["pct_change_diff"] < self._dataframe["prev_pct_change_diff"]
        # )

        # self._dataframe.loc[short, "signal"] = SHORT_SIGNAL

        ####

        # Sharpe: 2.31

        # self._dataframe["vix_pct_change"] = self._dataframe["vix close"].pct_change()

        # self._dataframe["spf_pct_change"] = self._dataframe["spf close"].pct_change()
        # self._dataframe["prev_spf_pct_change"] = self._dataframe[
        #     "spf_pct_change"
        # ].shift(1)

        # self._dataframe["vix_spf_pct_change_diff"] = (
        #     self._dataframe["vix_pct_change"] - self._dataframe["spf_pct_change"]
        # )

        # self._dataframe["prev_vix_spf_pct_change_diff"] = self._dataframe[
        #     "vix_spf_pct_change_diff"
        # ].shift(1)

        # # Filter us by underlying trend
        # self._dataframe["prev_close"] = self._dataframe["adj close"].shift(1)

        # long = (self._dataframe["adj close"] > self._dataframe["prev_close"]) & (
        #     self._dataframe["vix_spf_pct_change_diff"]
        #     < self._dataframe["prev_vix_spf_pct_change_diff"]
        # )

        # self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        # short = (self._dataframe["adj close"] < self._dataframe["prev_close"]) & (
        #     self._dataframe["vix_spf_pct_change_diff"]
        #     > self._dataframe["prev_vix_spf_pct_change_diff"]
        # )

        # self._dataframe.loc[short, "signal"] = SHORT_SIGNAL

        ####

        # Sharpe: 2.34

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

        Scenario A: VIX rises more than the S&P 500 falls (or VIX falls less than S&P 500 rises).

        Interpretation: The market is experiencing higher-than-usual fear or uncertainty.
        If the VIX rises sharply while the S&P 500 falls,
        it indicates that the market is anticipating increased volatility.
        This can occur during market corrections,
        economic uncertainty, or when significant news impacts investor sentiment.

        Scenario B: Both VIX and S&P 500 futures are falling, but the VIX falls less.

        Interpretation: This could suggest that although the market is calm (hence the VIX is falling),
        there’s still a degree of caution or hedging going on.
        The S&P 500 might be falling,
        but the VIX’s lesser drop indicates that traders aren’t fully confident
        that the market's decline will continue without increased volatility.

        NEGATIVE RESULT (SP500 CHANGE > VIX CHANGE):

        Scenario A: S&P 500 rises more than the VIX falls.
        Interpretation: The market is in a risk-on mode, meaning investors are feeling confident,
        and there’s a strong upward movement in the S&P 500.
        The VIX falling less in comparison might indicate that while there’s confidence,
        there’s still some underlying caution about potential risks.

        Scenario B: Both VIX and S&P 500 are rising, but the S&P 500 rises more.
        Interpretation: This could indicate a somewhat unusual market condition where the market is bullish,
        but there’s still significant hedging activity or concerns about future volatility,
        causing the VIX to rise even though the S&P 500 is also rising.

        Key Takeaways:

        Positive differences often indicate heightened fear or caution relative to the market movement.

        Negative differences suggest market confidence, but the
        degree of VIX movement relative to S&P 500 can reveal how much caution or hedging is present.
        """

        self._dataframe["vix_pct_change"] = self._dataframe["vix close"].pct_change()
        self._dataframe["spf_pct_change"] = self._dataframe["spf close"].pct_change()
        self._dataframe["prev_spf_pct_change"] = self._dataframe[
            "spf_pct_change"
        ].shift(1)

        self._dataframe["vix_spf_pct_change_diff"] = (
            self._dataframe["vix_pct_change"] - self._dataframe["spf_pct_change"]
        )

        self._dataframe["prev_vix_spf_pct_change_diff"] = self._dataframe[
            "vix_spf_pct_change_diff"
        ].shift(1)

        # Filter us by underlying trend
        self._dataframe["prev_close"] = self._dataframe["adj close"].shift(1)

        long = (
            (self._dataframe["adj close"] > self._dataframe["prev_close"])
            & (
                self._dataframe["vix_spf_pct_change_diff"]
                < self._dataframe["prev_vix_spf_pct_change_diff"]
            )
            & (
                self._dataframe["spf_pct_change"]
                > self._dataframe["prev_spf_pct_change"]
            )
        )

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self._dataframe["adj close"] < self._dataframe["prev_close"])
            & (
                self._dataframe["vix_spf_pct_change_diff"]
                > self._dataframe["prev_vix_spf_pct_change_diff"]
            )
            & (
                self._dataframe["spf_pct_change"]
                < self._dataframe["prev_spf_pct_change"]
            )
        )

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
