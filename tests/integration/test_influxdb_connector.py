from typing import TYPE_CHECKING

import pandas as pd
import pytest
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.settings import INFLUXDB_BUCKET, INFLUXDB_MEASUREMENT

if TYPE_CHECKING:
    from datetime import datetime


def test__get_last_record_date__with_no_data_available() -> None:
    """
    Test get_last_record_date when no data is available.

    Function should return None.
    """

    influxdb_connector = InfluxDbConnector()

    last_record_date = influxdb_connector.get_last_record_date()

    assert last_record_date is None


@pytest.mark.usefixtures("influxdb_client", "flush_influxdb_bucket", "dataframe")
def test__get_last_record_date__with_data_available(
    influxdb_client: InfluxDBClient,
    dataframe: pd.DataFrame,
) -> None:
    """
    Test get_last_record_date when data is available.

    Function should return last available record date.
    """

    control_last_record: datetime = dataframe.index[-1]
    control_last_record_date = control_last_record.date()

    with influxdb_client.write_api(write_options=SYNCHRONOUS) as write_api:
        write_api.write(
            bucket=str(INFLUXDB_BUCKET),
            record=dataframe,
            data_frame_measurement_name=INFLUXDB_MEASUREMENT,
            data_frame_tag_columns=["ticker"],
        )

    influxdb_connector = InfluxDbConnector()

    last_record_date = influxdb_connector.get_last_record_date()

    assert last_record_date == control_last_record_date
