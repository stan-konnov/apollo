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

1. Reading prices back (https://github.com/influxdata/influxdb-client-python) as DF!

2. Comments in API Connector.

3. Better configuration for client to consume env vars. (from_env_file())

4. Comments here.
"""


class InfluxDbConnector:
    """
    Influx Database Connector class.

    Acts as a wrapper around the InfluxDB Python client.
    """

    # Measurement name
    # for the price data
    measurement = "ohlcv"

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
                    data_frame_measurement_name=self.measurement,
                    data_frame_tag_columns=["ticker", "frequency"],
                )

    def get_last_record_date(self) -> str | None:
        """
        Get the last record date from the database.

        :returns: Last record date string or None if no records are found.
        """

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
            return (
                (tables[0].records[0]).get_time().strftime(DEFAULT_DATE_FORMAT)
                if tables and tables[0].records
                else None
            )
