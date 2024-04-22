from numpy import datetime64

from apollo.utils.common import to_default_date_string


def test__to_default_date_string__with_proper_inputs() -> None:
    """
    Test to_default_date_string with proper inputs.

    Function must return date string in YYYY-MM-DD format.
    """

    assert to_default_date_string(datetime64("2021-01-01")) == "2021-01-01"
