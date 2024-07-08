import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from apollo.settings import (
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)


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
                "INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_URL, INFLUXDB_TOKEN "
                "environment variables must be set.",
            )

        # Use me with "with" statement
        self.influxdb_client = InfluxDBClient(
            org=INFLUXDB_ORG,
            url=str(INFLUXDB_URL),
            token=INFLUXDB_TOKEN,
            timeout=30_000,  # Please make me environment variable
        )

    def write_price_data(self, price_data: pd.DataFrame) -> None:
        """
        Write price data to InfluxDB.

        :param price_data: Price dataframe to write to InfluxDB.
        """

        write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)

        write_api.write(
            bucket=str(INFLUXDB_BUCKET),
            record=price_data,
            data_frame_measurement_name="ohlcv",
            data_frame_tag_columns=["ticker"],
        )
