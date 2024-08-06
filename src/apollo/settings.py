from enum import Enum
from os import curdir, getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TICKER = getenv("TICKER")
VIX_TICKER = getenv("VIX_TICKER")
EXCHANGE = getenv("EXCHANGE")
STRATEGY = getenv("STRATEGY")
START_DATE = getenv("START_DATE")
END_DATE = getenv("END_DATE")
FREQUENCY = getenv("FREQUENCY")
MAX_PERIOD = getenv("MAX_PERIOD")

NO_SIGNAL = 0
LONG_SIGNAL = 1
SHORT_SIGNAL = -1

BACKTESTING_CASH_SIZE = 1000

ROOT_DIR = Path(curdir).resolve()
DATA_DIR = Path(f"{ROOT_DIR}/data")
PARM_DIR = Path(f"{ROOT_DIR}/parameters")
OPTP_DIR = Path(f"{ROOT_DIR}/parameters_opt")
PLOT_DIR = Path(f"{ROOT_DIR}/backtesting_plots")
BRES_DIR = Path(f"{ROOT_DIR}/backtesting_results")

DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_TIME_FORMAT = "%H:%M"

POSTGRES_URL = getenv("POSTGRES_URL")
INFLUXDB_ORG = getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = getenv("INFLUXDB_BUCKET")
INFLUXDB_URL = getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = getenv("INFLUXDB_TOKEN")
INFLUXDB_MEASUREMENT = getenv("INFLUXDB_MEASUREMENT")


class YahooApiFrequencies(Enum):
    """Frequency values accepted by Yahoo Finance API."""

    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


EXCHANGE_TIME_ZONE_AND_HOURS = {
    "NYSE": {
        "timezone": "America/New_York",
        "hours": {
            "open": "09:30",
            "close": "16:00",
        },
    },
}
