from apollo.connectors.database.influxdb_connector import InfluxDbConnector


def test__get_last_record_date__with_no_data_available() -> None:
    """
    Test get_last_record_date when no data is available.

    Function should return None.
    """

    influxdb_connector = InfluxDbConnector()

    result = influxdb_connector.get_last_record_date()

    assert result is None
