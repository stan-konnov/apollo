from datetime import datetime

import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from pytz import timezone

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_TIME_FORMAT,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)

"""
TODO:

https://stackoverflow.com/a/63628816/11675550

2. Identifying if we need to query data or read based on the API.

3. Reading prices back.

4. File structure:
        connectors/
            api/
                api_connector.py
            database/
                database_connector.py

5. Separate influx and postgres connectors (no need for inheritance).
"""


class DatabaseConnector:
    """
    Database Connector class.

    Is responsible for handling database
    operations to-from relational and time-series databases.

    Uses InfluxDB Client for time-series database operations.
    """

    def __init__(self) -> None:
        """Construct Database Connector."""

        if None in (INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_URL, INFLUXDB_TOKEN):
            raise ValueError(
                "EXCHANGE, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_URL, INFLUXDB_TOKEN "
                "environment variables must be set.",
            )

    def check_if_price_data_needs_update(self) -> bool:
        """
        Identify if prices need to be re-queried.

        We re-query prices if either:

        * No records are available in the database.
        * The last record is not from today and market is closed (data available).

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

            # Get the last record time if any
            last_record_date = (
                (tables[0].records[0]).get_time().strftime(DEFAULT_DATE_FORMAT)
                if tables and tables[0].records
                else None
            )

        if not last_record_date:
            return True

        # Get current date and time
        current_date = datetime.now(tz=timezone("UTC")).strftime(DEFAULT_DATE_FORMAT)
        current_time = datetime.now(tz=timezone("UTC")).strftime(DEFAULT_TIME_FORMAT)

        # Get the time in configured exchange
        time_in_relevant_exchange = datetime.now(
            tz=timezone(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
        ).strftime(DEFAULT_TIME_FORMAT)

        return (
            current_date > last_record_date and current_time > time_in_relevant_exchange
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
            write_api = client.write_api(write_options=SYNCHRONOUS)

            write_api.write(
                bucket=str(INFLUXDB_BUCKET),
                record=dataframe_to_write,
                data_frame_measurement_name="ohlcv",
                data_frame_tag_columns=["ticker", "frequency"],
            )
