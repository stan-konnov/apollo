import pandas as pd


class PostgresConnector:
    """
    Postgres Database connector class.

    Acts as a wrapper around Prisma Python client.
    """

    def write_backtesting_results(
        self,
        ticker: str,
        strategy: str,
        frequency: str,
        max_period: bool,
        parameters: dict[str, float],
        backtesting_results: pd.DataFrame,
        backtesting_end_date: str | None = None,
        backtesting_start_date: str | None = None,
    ) -> None:
        """
        Write backtesting results to the database.

        :param ticker: Instrument ticker symbol.
        :param strategy: Strategy name.
        :param frequency: Frequency of the data.
        :param max_period: Flag indicating if maximum available data was used.
        :param parameters: Best performing strategy parameters.
        :param backtesting_results: Backtesting results.
        :param backtesting_start_date: Start date of the backtesting period.
        :param backtesting_end_date: End date of the backtesting period.
        """
