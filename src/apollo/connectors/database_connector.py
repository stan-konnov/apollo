from influxdb_client import InfluxDBClient

from apollo.settings import (
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)


class DatabaseConnector:
    """
    Data Access Layer class.

    Is responsible for handling database
    operations to-from relational and time-series databases.

    Uses InfluxDB Client for time-series database operations.
    """

    def __init__(self) -> None:
        """Construct Data Access Layer."""

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
