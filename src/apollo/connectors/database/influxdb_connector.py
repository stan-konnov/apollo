import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)

"""
TODO:

1. Comments in API Connector.

2. Manage intraday prices from Yahoo API.
"""


class InfluxDbConnector:
    """
    Influx Database Connector class.

    Acts as a wrapper around the InfluxDB Python client.
    """

    # Measurement name
    # for the price data
    measurement = "ohlcv"

    def __init__(self) -> None:
        """
        Construct InfluxDB Connector.

        Define InfluxDB Client initialization parameters.
        """

        self.client_parameters = {
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

        with InfluxDBClient(**self.client_parameters) as client:
            # Copy and add frequency to the
            # dataframe to use as a tag value
            dataframe_to_write = dataframe.copy()
            dataframe_to_write["frequency"] = frequency

            # Create write API and write incoming dataframe
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                write_api.write(
                    bucket=str(INFLUXDB_BUCKET),
                    record=dataframe_to_write,
                    data_frame_measurement_name=self.measurement,
                    data_frame_tag_columns=["ticker", "frequency"],
                )

    def read_price_data(
        self,
        ticker: str,
        frequency: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """
        Read price data from the database.

        :param ticker: Ticker of the price data.
        :param frequency: Frequency of the price data.
        :param start_date: Start date of the price data (inclusive).
        :param end_date: End date of the price data (exclusive).
        :returns: Price dataframe read from the database.
        """

        with InfluxDBClient(**self.client_parameters) as client:
            # Create query API
            query_api = client.query_api()

            # Define query range
            query_range = "start:0"
            if start_date and end_date:
                query_range = f"start: {start_date}, stop: {end_date}"

            # Query the price data from the database
            query_statement = f"""
                from(bucket:"{INFLUXDB_BUCKET}")
                |> range({query_range})
                |> filter(fn: (r) =>
                        r.ticker == "{ticker}" and
                        r.frequency == "{frequency}" and
                        r._measurement == "{self.measurement}"
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
                            "high",
                            "low",
                            "close",
                            "adj close",
                            "volume",
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

            # Set the date column as index
            dataframe.set_index("date", inplace=True)

            # We always index by date,
            # therefore, we cast indices to datetime.
            dataframe.index = pd.to_datetime(dataframe.index)

            # Execute the query and return
            return dataframe

    def get_last_record_date(self) -> str | None:
        """
        Get the last record date from the database.

        :returns: Last record date string or None if no records are found.
        """

        with InfluxDBClient(**self.client_parameters) as client:
            # Create query API
            query_api = client.query_api()

            # Query the last record in the database
            query_statement = f"""
                from(bucket:"{INFLUXDB_BUCKET}")
                |> range(start:0)
                |> filter(fn: (r) =>
                        r._measurement == "ohlcv"
                    )
                |> last()
                """

            # Execute the query
            tables = query_api.query(query=query_statement, org=INFLUXDB_ORG)

            # Get the last record date string if any
            return (
                (tables[0].records[0]).get_time().strftime(DEFAULT_DATE_FORMAT)
                if tables and tables[0].records
                else None
            )
