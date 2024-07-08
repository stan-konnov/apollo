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

        self.influxdb_client = InfluxDBClient(
            org=INFLUXDB_ORG,
            url=str(INFLUXDB_URL),
            token=INFLUXDB_TOKEN,
        )

    def write_price_data(self, price_data: pd.DataFrame) -> None:
        """
        Write price data to InfluxDB.

        :param data: Price data to write to InfluxDB.
        """

        # Drop ticker column since we consider it as a tag
        clean_price_data = price_data.drop(columns=["ticker"])

        write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)

        write_api.write(
            bucket=str(INFLUXDB_BUCKET),
            record=clean_price_data,
            data_frame_measurement_name="ohlcv",
        )
