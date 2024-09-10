import pandas as pd


def precalculate_shared_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Precalculate shared values for the dataframe.

    :param dataframe: Dataframe to precalculate shared values for.
    :returns: Dataframe with precalculated shared values.
    """

    dataframe["prev_close"] = dataframe["adj close"].shift(1)

    return dataframe
