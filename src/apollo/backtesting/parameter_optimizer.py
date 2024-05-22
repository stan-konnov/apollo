from json import dump, loads
from logging import getLogger
from pathlib import Path
from sys import exit
from typing import ClassVar

import pandas as pd
from numpy import arange
from tqdm.contrib.itertools import product

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.settings import BRES_DIR, NO_SIGNAL, OPTP_DIR
from apollo.strategies.apo_mean_reversion import AbsolutePriceOscillatorMeanReversion
from apollo.strategies.arima_trend_mean_reversion import ARIMATrendMeanReversion
from apollo.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)
from apollo.strategies.logistic_regression_forecast import LogisticRegressionForecast
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)
from apollo.strategies.support_resistance_trend_following import (
    SupportResistanceTrendFollowing,
)
from apollo.strategies.swing_events_mean_reversion import SwingEventsMeanReversion
from apollo.utils.configuration import Configuration
from apollo.utils.types import (
    ParameterKeysAndCombinations,
    ParameterSet,
    StrategyNameToClassMap,
)

logger = getLogger(__name__)


class ParameterOptimizer:
    """
    Parameter Optimizer class.

    Consumes configuration object with various parameters that go into the strategy.
    Constructs ranges and combinations of parameters to optimize.
    Runs series of backtesting processes each for each set of parameters to optimize.
    Writes backtesting results and trades into files for further analysis.
    Writes optimized parameter set from sorted backtesting results.
    """

    # Represents a mapping between strategy name and strategy class
    # Is used to instantiate the strategy class based on configured name
    _strategy_name_to_class_map: ClassVar[StrategyNameToClassMap] = {
        "ARIMATrendMeanReversion":
            ARIMATrendMeanReversion,
        "SwingEventsMeanReversion":
            SwingEventsMeanReversion,
        "LogisticRegressionForecast":
            LogisticRegressionForecast,
        "SupportResistanceTrendFollowing":
            SupportResistanceTrendFollowing,
        "LinearRegressionChannelMeanReversion":
            LinearRegressionChannelMeanReversion,
        "AbsolutePriceOscillatorMeanReversion":
            AbsolutePriceOscillatorMeanReversion,
        "SkewnessKurtosisVolatilityTrendFollowing":
            SkewnessKurtosisVolatilityTrendFollowing,
    }

    def __init__(self) -> None:
        """
        Construct Parameter Optimizer.

        Instantiate configuration that consumes environment
        variables and parses strategy parameters file.

        Define a path to individual strategy directory
        to store backtesting results and trades.

        Create output directories for results,
        trades, and optimized parameters if they do not exist.
        """

        self._configuration = Configuration()

        self.strategy_dir = Path(
            f"{BRES_DIR}/"
            f"{self._configuration.ticker}-"
            f"{self._configuration.strategy}-"
            f"{self._configuration.start_date}-"
            f"{self._configuration.end_date}",
        )

        self._create_output_directories()

    def process(self) -> None:
        """Run the optimization process."""

        # Initialize the backtesting results dataframe
        # to populate with results of each backtesting run
        backtesting_results_dataframe = pd.DataFrame()

        # Instantiate the API connector
        api_connector = YahooApiConnector(
            ticker=self._configuration.ticker,
            start_date=self._configuration.start_date,
            end_date=self._configuration.end_date,
        )

        # Request or read the prices
        dataframe = api_connector.request_or_read_prices()

        # Instantiate the strategy class by typecasting
        # the strategy name from configuration to the corresponding class
        strategy_name = self._configuration.strategy
        strategy_class = type(
            strategy_name,
            (self._strategy_name_to_class_map[strategy_name],),
            {},
        )

        # Extract the parameter set from the configuration
        parameter_set = self._configuration.parameter_set

        # Build keys and combinations of parameters to optimize
        keys, combinations = self._construct_parameter_combinations(
            parameter_set,
        )

        # Iterate over each combination of parameters
        for combination in combinations:
            # We copy the dataframe to have a clean
            # set of prices for each combination we are testing
            dataframe_to_test = dataframe.copy()

            # Construct back a dictionary with parameter names and values
            combination_to_test = {
                **dict(zip(keys, combination)),
            }

            # Extract the strategy-specific parameters
            strategy_specific_parameters = {
                key: combination_to_test[key]
                for key in parameter_set["strategy_specific_parameters"]
            }

            # Instantiate the strategy with the parameters to test
            #
            # NOTE:
            # Due to the fact that strategy specific parameters
            # are different for each strategy, we do not have the
            # way to properly type them in the BaseStrategy class
            # Therefore, we resolve to extracting them from produced combinations
            # and spreading them as keyword arguments to the strategy constructor
            #
            # Clearly, this is not the most elegant or type-safe solution
            # In such, every strategy is responsible for validating the parameters
            try:
                strategy_instance = strategy_class(
                    dataframe=dataframe_to_test,
                    window_size=int(combination_to_test["window_size"]),
                    **strategy_specific_parameters,
                )

            except (ValueError, TypeError):
                # Of course, we want to exit if parameters are misconfigured
                logger.exception("Parameters misconfigured, see traceback")
                exit(1)

            # Model the trading signals
            strategy_instance.model_trading_signals()

            # Skip this run if there are no signals
            if (dataframe_to_test["signal"] == NO_SIGNAL).all():
                continue

            # Instantiate the backtesting runner and run the backtesting process
            backtesting_runner = BacktestingRunner(
                dataframe=dataframe_to_test,
                strategy_name=strategy_name,
                # NOTE: cash_size is non-optimized parameter (yet)
                # and therefore is hardcoded to the value from parameter set
                lot_size_cash=parameter_set["cash_size"],
                sl_volatility_multiplier=combination_to_test[
                    "sl_volatility_multiplier"
                ],
                tp_volatility_multiplier=combination_to_test[
                    "tp_volatility_multiplier"
                ],
            )

            stats = backtesting_runner.run()

            # Construct a Dataframe with the results of this run
            this_run_results = pd.DataFrame(stats).transpose()

            # Preserve the parameters used for this run
            this_run_results["parameters"] = str(
                {
                    "frequency": parameter_set["frequency"],
                    "cash_size": parameter_set["cash_size"],
                    **combination_to_test,
                },
            )

            # Append the results of this run to the backtesting results dataframe
            if backtesting_results_dataframe.empty:
                backtesting_results_dataframe = this_run_results

            else:
                backtesting_results_dataframe = pd.concat(
                    [backtesting_results_dataframe, this_run_results],
                )

        # Output the results to a file and create optimized parameters file
        self._output_results(backtesting_results_dataframe)

    def _construct_parameter_combinations(
        self,
        parameter_set: ParameterSet,
    ) -> ParameterKeysAndCombinations:
        """
        Construct parameter sets for each combination of parameters.

        :param parameters: TypedDict with parameter specifications.
        :returns: Iterable of tuples where each tuple contains a set of parameters.
        """

        # Extract the parameter ranges
        parameter_ranges = {
            key: self._get_combination_ranges(
                value["range"][0],
                value["range"][1],
                value["step"],
            )
            for key, value in parameter_set.items()
            if (isinstance(value, dict) and "range" in value)
        }

        # Generate all possible combinations of parameter values
        return parameter_ranges.keys(), product(*parameter_ranges.values())

    def _get_combination_ranges(
        self,
        range_min: float,
        range_max: float,
        range_step: float,
    ) -> pd.Series:
        """
        Generate a range of floats for every parameter.

        :param range_min: The start of the range.
        :param range_max: The end of the range.
        :param step: The step size.
        :returns: Series of rounded floating-point numbers.
        """

        # NOTE: we round the values to avoid floating-point arithmetic errors
        return pd.Series(
            arange(range_min, range_max + range_step / 2, range_step),
        ).round(10)

    def _output_results(self, results_dataframe: pd.DataFrame) -> None:
        """
        Prepare and write the results and trades to a file system.

        Write optimized parameters file.

        :param results_dataframe: DataFrame with backtesting results.
        """

        # Sort the results by total return, sharpe ratio, and number of trades
        results_dataframe.sort_values(
            ["Return [%]", "Sharpe Ratio", "# Trades"],
            ascending=False,
            inplace=True,
        )

        # Reset the indices to clean up the dataframe after concatenation
        results_dataframe.reset_index(drop=True, inplace=True)

        # Grab the best performing trades
        trades_dataframe = results_dataframe.iloc[0]["_trades"]

        # Bring returns to more human readable format
        trades_dataframe["ReturnPct"] = trades_dataframe["ReturnPct"] * 100

        # Drop columns that are not needed for further analysis
        results_dataframe.drop(
            columns=[
                "Start",
                "End",
                "Duration",
                "Profit Factor",
                "Expectancy [%]",
                "_strategy",
                "_equity_curve",
                "_trades",
            ],
            inplace=True,
        )

        # Extract the best performing parameters as JSON
        # and prepare them for writing to a file
        optimized_parameters = results_dataframe.iloc[0]["parameters"]
        optimized_parameters = str(optimized_parameters).replace("'", '"')
        optimized_parameters = loads(optimized_parameters)

        # Write the results and parameters to files
        self._write_result_files(
            trades_dataframe,
            results_dataframe,
            optimized_parameters,
        )

    def _create_output_directories(self) -> None:
        """
        Create output directories if they do not exist.

        Create main results directory.
        Create individual strategy directory.
        Create optimized parameters directory.
        """

        for path in [BRES_DIR, self.strategy_dir, OPTP_DIR]:
            if not Path.is_dir(path):
                path.mkdir(parents=True, exist_ok=True)

    def _write_result_files(
        self,
        trades_dataframe: pd.DataFrame,
        results_dataframe: pd.DataFrame,
        optimized_parameters: dict[str, str | int | float],
    ) -> None:
        """
        Write the results, trades and parameters to files.

        :param trades_dataframe: Dataframe with trades.
        :param results_dataframe: Dataframe with backtesting results.
        :param optimized_parameters: Dictionary with optimized parameters.
        """

        trades_dataframe.to_csv(f"{self.strategy_dir}/trades.csv")
        results_dataframe.to_csv(f"{self.strategy_dir}/results.csv")

        with Path.open(
            Path(f"{OPTP_DIR}/{self._configuration.strategy}.json"),
            "w",
        ) as file:
            dump(optimized_parameters, file, indent=4)
