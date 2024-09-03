import pandas as pd

from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL

"""
TODO:

1. Make sure rows are not dropped for strategies
   that rely on incomplete enhancing data.

2. Avoid populating NaN in enhancers as calculations
   will anyways lead to NaNs.

3. Reoptimize SkewKurtVol.

4. Backtest new strategy and Futures enhancing on full period.
"""


class FuturesEnhancedStrategy:
    """
    Futures Enhanced Strategy class.

    Massive work in progress.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Construct VIX Futures Enhanced Strategy.

        :param dataframe: Dataframe with price data.
        """

        # Mark Futures enhanced signals to the dataframe
        dataframe["spf_signal"] = NO_SIGNAL

        # Initialize necessary columns with 0s
        dataframe["spf_prev_open"] = 0
        dataframe["spf_prev_close"] = 0

        # Compute necessary columns
        # only in case if data is present
        dataframe.loc[dataframe["spf open"].notna(), "spf_prev_open"] = dataframe[
            "spf open"
        ].shift(1)

        dataframe.loc[dataframe["spf close"].notna(), "spf_prev_close"] = dataframe[
            "spf close"
        ].shift(
            1,
        )

        necessary_columns_present = (
            dataframe["spf open"].notna()
            & dataframe["spf close"].notna()
            & dataframe["spf_prev_open"].notna()
            & dataframe["spf_prev_close"].notna()
        )

        long = (
            necessary_columns_present
            & (dataframe["spf open"] > dataframe["spf_prev_open"])
            & (dataframe["spf close"] < dataframe["spf_prev_close"])
            & (dataframe["spf close"] < dataframe["spf open"])
        )

        dataframe.loc[long, "spf_signal"] = LONG_SIGNAL

        short = (
            necessary_columns_present
            & (dataframe["spf open"] < dataframe["spf_prev_open"])
            & (dataframe["spf close"] > dataframe["spf_prev_close"])
            & (dataframe["spf close"] > dataframe["spf open"])
        )

        dataframe.loc[short, "spf_signal"] = SHORT_SIGNAL
