from typing import TYPE_CHECKING

import pandas as pd
import pytest
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.settings import (
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    TICKER,
    YahooApiFrequencies,
)

if TYPE_CHECKING:
    from datetime import datetime


def test__get_last_record_date__with_no_data_available() -> None:
    """
    Test get_last_record_date when no data is available.

    InfluxDbConnector should return None.
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

    InfluxDbConnector should return last available record date.
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


@pytest.mark.usefixtures("influxdb_client", "flush_influxdb_bucket", "dataframe")
def test__write_price_data__for_correctly_writing_dataframe(
    influxdb_client: InfluxDBClient,
    dataframe: pd.DataFrame,
) -> None:
    """
    Test write_price_data for correctly writing dataframe.

    Dataframe must be available in the database after writing.
    """

    frequency = YahooApiFrequencies.ONE_DAY.value

    influxdb_connector = InfluxDbConnector()
    influxdb_connector.write_price_data(
        frequency=frequency,
        dataframe=dataframe,
    )

    query_api = influxdb_client.query_api()
    query_statement = f"""
        from(bucket:"{INFLUXDB_BUCKET}")
        |> range(start:0)
        |> filter(fn: (r) =>
                r.ticker == "{TICKER}" and
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

    control_dataframe: pd.DataFrame = query_api.query_data_frame(
        query=query_statement,
        org=INFLUXDB_ORG,
    )

    control_dataframe.drop(columns=["result", "table"], inplace=True)
    control_dataframe["date"] = control_dataframe["date"].dt.tz_localize(None)
    control_dataframe.set_index("date", inplace=True)

    # Reset columns on control dataframe to
    # factor in influx sorting columns alphabetically
    control_dataframe = control_dataframe[dataframe.columns]

    pd.testing.assert_frame_equal(dataframe, control_dataframe)


@pytest.mark.usefixtures("influxdb_client", "flush_influxdb_bucket", "dataframe")
def test__read_price_data__for_reading_all_available_data(
    influxdb_client: InfluxDBClient,
    dataframe: pd.DataFrame,
) -> None:
    """
    Test read_price_data for reading all available data.

    InfluxDbConnector should return all available data in the database.
    InfluxDbConnector should remove influx columns.
    """

    frequency = YahooApiFrequencies.ONE_DAY.value
    dataframe["frequency"] = frequency

    with influxdb_client.write_api(write_options=SYNCHRONOUS) as write_api:
        write_api.write(
            bucket=str(INFLUXDB_BUCKET),
            record=dataframe,
            data_frame_measurement_name=INFLUXDB_MEASUREMENT,
            data_frame_tag_columns=["ticker", "frequency"],
        )

    dataframe.drop(columns=["frequency"], inplace=True)

    influxdb_connector = InfluxDbConnector()

    control_dataframe = influxdb_connector.read_price_data(
        ticker=str(TICKER),
        frequency=frequency,
    )

    assert "table" not in control_dataframe.columns
    assert "result" not in control_dataframe.columns

    control_dataframe = control_dataframe[dataframe.columns]

    pd.testing.assert_frame_equal(dataframe, control_dataframe)


@pytest.mark.usefixtures("influxdb_client", "flush_influxdb_bucket", "dataframe")
def test__read_price_data__for_reading_data_slice(
    influxdb_client: InfluxDBClient,
    dataframe: pd.DataFrame,
) -> None:
    """
    Test read_price_data for reading data slice.

    InfluxDbConnector should return data slice from the database.
    InfluxDbConnector should remove influx columns.
    """

    start_date = "2007-01-10"
    end_date = "2007-01-20"

    frequency = YahooApiFrequencies.ONE_DAY.value
    dataframe["frequency"] = frequency

    with influxdb_client.write_api(write_options=SYNCHRONOUS) as write_api:
        write_api.write(
            bucket=str(INFLUXDB_BUCKET),
            record=dataframe,
            data_frame_measurement_name=INFLUXDB_MEASUREMENT,
            data_frame_tag_columns=["ticker", "frequency"],
        )

    dataframe.drop(columns=["frequency"], inplace=True)
    dataframe = dataframe.loc[start_date:end_date]

    influxdb_connector = InfluxDbConnector()

    control_dataframe = influxdb_connector.read_price_data(
        ticker=str(TICKER),
        frequency=frequency,
        start_date=start_date,
        end_date=end_date,
    )

    assert "table" not in control_dataframe.columns
    assert "result" not in control_dataframe.columns

    control_dataframe = control_dataframe[dataframe.columns]

    pd.testing.assert_frame_equal(dataframe, control_dataframe)
