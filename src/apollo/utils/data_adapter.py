import pandas as pd


class DataAdapter:
    """
    Data Adapter class.

    Servers the purpose of preparing the
    price data for saving into storage and calculations.

    TODO: break down API connector, preparing of data, and saving
    into separate classes. Build DataProvider class to yield data.
    """

    @staticmethod
    def prepare_price_data(ticker: str, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare price data.

        Reset indices, cast columns to lowercase.
        Set indices back to date column.
        Add ticker column.

        Adjust OHLCV values based on adjusted close
        to avoid inconsistencies around stock splits and dividends.

        :param ticker: Ticker to insert into dataframe.
        :param dataframe: Dataframe with price data to prepare.
        :returns: Prepared dataframe.
        """

        dataframe.reset_index(inplace=True)
        dataframe.columns = dataframe.columns.str.lower()

        dataframe.insert(0, "ticker", ticker)
        dataframe.set_index("date", inplace=True)

        adjustment_factor = dataframe["adj close"] / dataframe["close"]

        dataframe["adj open"] = dataframe["open"] * adjustment_factor
        dataframe["adj high"] = dataframe["high"] * adjustment_factor
        dataframe["adj low"] = dataframe["low"] * adjustment_factor
        dataframe["adj volume"] = dataframe["volume"] / (adjustment_factor)

        return dataframe
