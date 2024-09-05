import pandas as pd


def precalculate_shared_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Precalculate shared values for the dataframe.

    :param dataframe: The dataframe to precalculate shared values for.
    :returns: The dataframe with precalculated shared values.
    """

    dataframe["prev_close"] = dataframe["adj close"].shift(1)

    return dataframe
