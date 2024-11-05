from enum import Enum
from os import curdir, getenv
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

load_dotenv()

TICKER = getenv("TICKER")
EXCHANGE = getenv("EXCHANGE")
STRATEGY = getenv("STRATEGY")
START_DATE = getenv("START_DATE")
END_DATE = getenv("END_DATE")
FREQUENCY = getenv("FREQUENCY")
MAX_PERIOD = getenv("MAX_PERIOD")
VIX_TICKER = getenv("VIX_TICKER")
SP500_FUTURES_TICKER = getenv("SP500_FUTURES_TICKER")
SP500_COMPONENTS_URL = getenv("SP500_COMPONENTS_URL")
SCREENING_WINDOW_SIZE = getenv("SCREENING_WINDOW_SIZE")
SUPPORTED_DATA_ENHANCERS = getenv("SUPPORTED_DATA_ENHANCERS")
SCREENING_LIQUIDITY_THRESHOLD = getenv("SCREENING_LIQUIDITY_THRESHOLD")

NO_SIGNAL = 0
LONG_SIGNAL = 1
SHORT_SIGNAL = -1

BACKTESTING_CASH_SIZE = 1000
MISSING_DATA_PLACEHOLDER = np.inf

ROOT_DIR = Path(curdir).resolve()
PARM_DIR = Path(f"{ROOT_DIR}/parameters")
PLOT_DIR = Path(f"{ROOT_DIR}/backtesting_plots")
TRDS_DIR = Path(f"{ROOT_DIR}/backtesting_trades")

DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_TIME_FORMAT = "%H:%M"

POSTGRES_URL = getenv("POSTGRES_URL")
INFLUXDB_URL = getenv("INFLUXDB_URL")
INFLUXDB_ORG = getenv("INFLUXDB_ORG")
INFLUXDB_TOKEN = getenv("INFLUXDB_TOKEN")
INFLUXDB_BUCKET = getenv("INFLUXDB_BUCKET")
INFLUXDB_MEASUREMENT = getenv("INFLUXDB_MEASUREMENT")


class PriceDataFrequency(Enum):
    """
    Frequency of the price data.

    Denotes currently supported time frames.
    """

    ONE_DAY = "1d"


class ParameterOptimizerMode(Enum):
    """
    Parameter optimizer mode of operation.

    Denotes whether optimization process
    should run over single or multiple strategies.
    """

    SINGLE_STRATEGY = "single_strategy"
    MULTIPLE_STRATEGIES = "multiple_strategies"


EXCHANGE_TIME_ZONE_AND_HOURS = {
    "NYSE": {
        "timezone": "America/New_York",
        "hours": {
            "open": "09:30",
            "close": "16:00",
        },
    },
}
