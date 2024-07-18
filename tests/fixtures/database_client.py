from typing import Generator

import pytest
from influxdb_client import InfluxDBClient
from prisma import Prisma

from apollo.settings import (
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
)


@pytest.fixture(name="influxdb_client", scope="session")
def influxdb_client() -> Generator[InfluxDBClient, None, None]:
    """Initialize InfluxDB client to use in tests."""

    client = InfluxDBClient(
        url=str(INFLUXDB_URL),
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG,
    )

    yield client

    client.close()


@pytest.fixture(name="flush_influxdb_bucket", autouse=True)
def _flush_influxdb_bucket(influxdb_client: InfluxDBClient) -> None:
    """
    Flush the InfluxDB bucket after each test.

    :param influxdb_client: The InfluxDB client.
    """

    delete_api = influxdb_client.delete_api()

    delete_api.delete(
        start="1970-01-01T00:00:00Z",
        stop="2100-01-01T00:00:00Z",
        predicate=f'_measurement="{INFLUXDB_MEASUREMENT}"',
        bucket=str(INFLUXDB_BUCKET),
        org=INFLUXDB_ORG,
    )


@pytest.fixture(name="prisma_client", scope="session")
def prisma_client() -> Prisma:
    """Initialize Prisma client to use in tests."""

    return Prisma()


@pytest.fixture(name="flush_postgres_database", autouse=True)
def _flush_postgres_database(prisma_client: Prisma) -> None:
    """
    Flush the Postgres database after each test.

    :param prisma_client: The Prisma client.
    """

    prisma_client.connect()

    prisma_client.execute_raw(
        """
        DO $$ DECLARE
            r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema() AND tablename != '_prisma_migrations') LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """,  # noqa: E501
    )

    prisma_client.disconnect()
