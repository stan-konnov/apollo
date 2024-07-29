from datetime import date
from logging import getLogger

import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from urllib3.exceptions import ReadTimeoutError

from apollo.settings import (
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)

logger = getLogger(__name__)


class InfluxDbConnector:
    """
    Influx Database Connector class.

    Acts as a wrapper around the InfluxDB Python client.
    """

    def __init__(self) -> None:
        """
        Construct InfluxDB Connector.

        Define InfluxDB Client initialization parameters.
        """

        self._client_parameters = {
            "org": INFLUXDB_ORG,
            "url": str(INFLUXDB_URL),
            "token": INFLUXDB_TOKEN,
        }

    def write_price_data(
        self,
        frequency: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Write price data to the database.

        :param frequency: Frequency of the price data.
        :param dataframe: Price dataframe to write to the database.
        """

        try:
            with InfluxDBClient(**self._client_parameters) as client:
                # Copy and add frequency to the
                # dataframe to use as a tag value
                dataframe_to_write = dataframe.copy()
                dataframe_to_write["frequency"] = frequency

                # Create write API and write incoming dataframe
                with client.write_api(write_options=SYNCHRONOUS) as write_api:
                    write_api.write(
                        bucket=str(INFLUXDB_BUCKET),
                        record=dataframe_to_write,
                        data_frame_measurement_name=INFLUXDB_MEASUREMENT,
                        data_frame_tag_columns=["ticker", "frequency"],
                    )

        except ReadTimeoutError:
            # NOTE: on first-time write InfluxDB may raise a ReadTimeoutError
            # due to the internals of it's interaction with urllib3
            # This is a known issue, yet, solutions provided
            # in influxdb client documentation do not work
            # This does not affect the write operation
            # and, therefore, can be ignored
            logger.info(
                "Hitting ReadTimeoutError on InfluxDB write. Passing through.",
            )

    def read_price_data(
        self,
        ticker: str,
        frequency: str,
        start_date: str,
        end_date: str,
        max_period: bool,
    ) -> pd.DataFrame:
        """
        Read price data from the database.

        :param ticker: Ticker to read prices data for.
        :param frequency: Frequency of read price data.
        :param start_date: Start point to read price data from (inclusive).
        :param end_date: End point until which to read prices data (exclusive).
        :param max_period: Flag to read the maximum available period of price data.
        :returns: Dataframe with price data.
        """

        with InfluxDBClient(**self._client_parameters) as client:
            # Create query API
            query_api = client.query_api()

            # Define query range
            # depending on the max period flag
            query_range = (
                "start:0" if max_period else f"start: {start_date}, stop: {end_date}"
            )

            # Query the price data from the database
            query_statement = f"""
                from(bucket:"{INFLUXDB_BUCKET}")
                |> range({query_range})
                |> filter(fn: (r) =>
                        r.ticker == "{ticker}" and
                        r.frequency == "{frequency}" and
                        r._measurement == "{INFLUXDB_MEASUREMENT}"
                    )
                |> pivot(
                        rowKey: ["_time"],
                        columnKey: ["_field"],
                        valueColumn: "_value"
                    )
                |> keep(
                        columns: [
                            "ticker",
                            "open",
                            "adj open",
                            "high",
                            "adj high",
                            "low",
                            "adj low",
                            "close",
                            "adj close",
                            "volume",
                            "adj volume",
                            "_time",
                        ]
                    )
                |> rename(columns: {'{_time: "date"}'})
                """

            # Execute the query
            dataframe: pd.DataFrame = query_api.query_data_frame(
                query=query_statement,
                org=INFLUXDB_ORG,
            )

            # Drop unnecessary influx columns
            dataframe.drop(columns=["result", "table"], inplace=True)

            # Remove time and timezone information from date
            # as we do not yet work with multiple frequencies and exchanges
            dataframe["date"] = dataframe["date"].dt.tz_localize(None)

            # Set the date column as index
            dataframe.set_index("date", inplace=True)

            # Execute the query and return
            return dataframe

    def get_last_record_date(self, ticker: str, frequency: str) -> date | None:
        """
        Get the last record date from the database.

        :param ticker: Ticker of the last record date.
        :param frequency: Frequency of the last record date.
        :returns: Last record date or None if no records are found.
        """

        with InfluxDBClient(**self._client_parameters) as client:
            # Create query API
            query_api = client.query_api()

            # Query the last record in the database
            query_statement = f"""
                from(bucket:"{INFLUXDB_BUCKET}")
                |> range(start:0)
                |> filter(fn: (r) =>
                        r.ticker == "{ticker}" and
                        r.frequency == "{frequency}" and
                        r._measurement == "{INFLUXDB_MEASUREMENT}"
                    )
                |> last()
                """

            # Execute the query
            tables = query_api.query(query=query_statement, org=INFLUXDB_ORG)

            # Get the last record date string if any
            return (
                (tables[0].records[0]).get_time().date()
                if tables and tables[0].records
                else None
            )
