from datetime import datetime

import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from zoneinfo import ZoneInfo

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)
from apollo.utils.market_hours import check_if_data_available_from_exchange

"""
TODO:

1. Reading prices back (https://github.com/influxdata/influxdb-client-python) as DF!

2. Comments in API Connector.

3. Better configuration for client to consume env vars. (from_env_file())

3. Comments here.

4. File structure:
        connectors/
            api/
                api_connector.py
            database/
                database_connector.py

5. Separate influx and postgres connectors (no need for inheritance).

6. Measurement as class variable.
"""


class DatabaseConnector:
    """
    Database Connector class.

    Is responsible for handling database
    operations to-from relational and time-series databases.

    Uses InfluxDB Client for time-series database operations.
    """

    def __init__(self) -> None:
        """
        Construct Database Connector.

        :raises ValueError: If required environment variables are not set.
        """

        if None in (INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_URL, INFLUXDB_TOKEN):
            raise ValueError(
                "INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_URL, INFLUXDB_TOKEN "
                "environment variables must be set.",
            )

    def check_if_price_data_needs_update(self) -> bool:
        """
        Identify if prices need to be re-queried.

        We re-query prices if either:

        * No records are available in the database.
        * Last record date is before previous business day.
        * Last record date is previous business day and data available from exchange.

        :returns: Boolean indicating if prices need to be re-queried.
        """

        last_record_date: str | None

        with InfluxDBClient(
            org=INFLUXDB_ORG,
            url=str(INFLUXDB_URL),
            token=INFLUXDB_TOKEN,
        ) as client:
            # Create query API
            query_api = client.query_api()

            # Query the last record in the database
            query_statement = f"""
                from(bucket:"{INFLUXDB_BUCKET}")
                |> range(start:0)
                |> filter(fn: (r) =>
                    r._measurement == "ohlcv")
                |> last()
                """

            # Execute the query
            tables = query_api.query(query=query_statement, org="apollo")

            # Get the last record date string if any
            last_record_date = (
                (tables[0].records[0]).get_time().strftime(DEFAULT_DATE_FORMAT)
                if tables and tables[0].records
                else None
            )

        # Re-query prices
        # if no records are available
        if not last_record_date:
            return True

        # Otherwise, get current date string
        current_date = datetime.now(tz=ZoneInfo("UTC")).strftime(
            DEFAULT_DATE_FORMAT,
        )

        # Check if the configured exchange is closed
        data_available_from_exchange = check_if_data_available_from_exchange()

        # Re-query prices
        return last_record_date < current_date or (
            last_record_date == current_date and data_available_from_exchange
        )

    def write_price_data(
        self,
        frequency: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Write price data to InfluxDB.

        :param frequency: Frequency of the price data.
        :param dataframe: Price dataframe to write to InfluxDB.
        """

        with InfluxDBClient(
            org=INFLUXDB_ORG,
            url=str(INFLUXDB_URL),
            token=INFLUXDB_TOKEN,
        ) as client:
            # Copy and add frequency to the
            # dataframe to use as a tag value
            dataframe_to_write = dataframe.copy()
            dataframe_to_write["frequency"] = frequency

            # Create write API and write incoming dataframe
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                write_api.write(
                    bucket=str(INFLUXDB_BUCKET),
                    record=dataframe_to_write,
                    data_frame_measurement_name="ohlcv",
                    data_frame_tag_columns=["ticker", "frequency"],
                )
