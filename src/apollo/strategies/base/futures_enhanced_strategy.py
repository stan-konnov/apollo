import pandas as pd

from apollo.settings import (
    LONG_SIGNAL,
    MISSING_DATA_PLACEHOLDER,
    NO_SIGNAL,
    SHORT_SIGNAL,
)

"""
TODO:

1. Backtest all strategies with this enhancement (Swing Events + WSI left).

2. Move calculations to a calculator file.

3. Make sure VIX enhanced strategy does not drop rows.

4. Make sure VIX EC strategy does not drop rows.

5. Experiment with VIX FUT CD strategy as enhancer.

6. Make this strategy a separate strategy.
"""


class FuturesEnhancedStrategy:
    """
    Futures Enhanced Strategy class.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Construct VIX Futures Enhanced Strategy.

        :param dataframe: Dataframe with price data.
        """

        # REWORK THIS COMMENT
        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, need to check against NaNs after calculation,
        # since calculating over missing data results in NaNs that are dropped

        # Mark futures enhanced signals to the dataframe
        dataframe["spf_signal"] = NO_SIGNAL

        # Initialize necessary columns with 0
        dataframe["spf_prev_open"] = 0
        dataframe["spf_prev_close"] = 0

        # Shift open and close prices only if the data is present
        dataframe.loc[
            dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
            "spf_prev_open",
        ] = dataframe["spf open"].shift(1)

        dataframe.loc[
            dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
            "spf_prev_close",
        ] = dataframe["spf close"].shift(1)

        long = (
            (dataframe["spf open"] > dataframe["spf_prev_open"])
            & (dataframe["spf close"] < dataframe["spf_prev_close"])
            & (dataframe["spf close"] < dataframe["spf open"])
        )

        dataframe.loc[long, "spf_signal"] = LONG_SIGNAL

        short = (
            (dataframe["spf open"] < dataframe["spf_prev_open"])
            & (dataframe["spf close"] > dataframe["spf_prev_close"])
            & (dataframe["spf close"] > dataframe["spf open"])
        )

        dataframe.loc[short, "spf_signal"] = SHORT_SIGNAL
