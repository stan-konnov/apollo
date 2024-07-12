from typing import Generator

import pytest
from influxdb_client import InfluxDBClient

from apollo.settings import (
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)


@pytest.fixture(name="influxdb_client", scope="module")
def influxdb_client() -> Generator[InfluxDBClient, None, None]:
    """Initialize InfluxDB client to use in tests."""

    client = InfluxDBClient(
        url=str(INFLUXDB_URL),
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG,
    )

    yield client

    client.close()


@pytest.fixture(name="flush_influxdb_bucket")
def _flush_influxdb_bucket(influxdb_client: InfluxDBClient) -> None:
    """
    Flush the InfluxDB bucket after each test.

    :param influxdb_client: The InfluxDB client.
    """

    delete_api = influxdb_client.delete_api()

    start = "1970-01-01T00:00:00Z"
    stop = "2100-01-01T00:00:00Z"

    delete_api.delete(
        start,
        stop,
        '_measurement="test_measurement"',
        bucket=str(INFLUXDB_BUCKET),
        org=INFLUXDB_ORG,
    )
