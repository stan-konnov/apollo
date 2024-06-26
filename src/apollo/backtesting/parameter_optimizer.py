from itertools import product
from json import dump, loads
from logging import getLogger
from multiprocessing import Pool, cpu_count
from pathlib import Path
from sys import exit
from typing import Union

import pandas as pd
from numpy import arange

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.backtesting.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.settings import BRES_DIR, NO_SIGNAL, OPTP_DIR
from apollo.utils.configuration import Configuration
from apollo.utils.types import (
    ParameterCombinations,
    ParameterKeysAndCombinations,
    ParameterSet,
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

    Is multiprocessing capable and runs in parallel.
    """

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

    def process_in_parallel(self) -> None:
        """Run the optimization process in parallel."""

        # Instantiate the API connector
        api_connector = YahooApiConnector(
            ticker=self._configuration.ticker,
            start_date=self._configuration.start_date,
            end_date=self._configuration.end_date,
        )

        # Request or read the prices
        price_dataframe = api_connector.request_or_read_prices()

        # Get the number of available CPU cores
        available_cores = cpu_count()

        # Extract the parameter set from the configuration
        parameter_set = self._configuration.parameter_set

        # Build keys and combinations of parameters to optimize
        keys, combinations = self._construct_parameter_combinations(
            parameter_set,
        )

        # Break down combinations into equal batches
        batches = self._batch_combinations(available_cores, combinations)

        # Create arguments to supply to each process
        batch_arguments = [
            (batch, price_dataframe, parameter_set, keys) for batch in batches
        ]

        # Process each batch in parallel
        with Pool(processes=available_cores) as pool:
            results = pool.starmap(self._process, batch_arguments)

            # Concatenate the results from each process
            combined_results = pd.concat(results)

            # Output the results to a file and create optimized parameters file
            self._output_results(combined_results)

    def _batch_combinations(
        self,
        batch_count: int,
        combinations: ParameterCombinations,
    ) -> list[ParameterCombinations]:
        """
        Split combinations into equal batches.

        :param batch_count: Number of batches to split combinations into.
        :param combinations: Iterable of tuples with parameter combinations.
        :returns: List of batches with parameter combinations.
        """

        # Cast the product to a list
        combinations = list(combinations)

        # Calculate the total number of combinations
        combinations_count = len(combinations)

        # Calculate the base size of each batch
        batch_base_size = combinations_count // batch_count

        # Calculate the size of the remainder batch
        remainder_batch_size = combinations_count % batch_count

        start_index = 0
        batches_to_return = []

        # Iterate over the number of batches
        for i in range(batch_count):
            # Calculate the current batch size
            current_batch_size = batch_base_size + (
                1 if i < remainder_batch_size else 0
            )

            # Slice and append the current batch
            batches_to_return.append(
                combinations[start_index : start_index + current_batch_size],
            )

            # Update the start index for the next batch
            start_index += current_batch_size

        return batches_to_return

    def _process(
        self,
        combinations: ParameterCombinations,
        price_dataframe: pd.DataFrame,
        parameter_set: ParameterSet,
        keys: list[str],
    ) -> pd.DataFrame:
        """
        Run the optimization process.

        :param combinations: Iterable of tuples with parameter combinations.
        :param price_dataframe: Dataframe with price data.
        :param parameter_set: parameter specifications.
        :param keys: List of parameter keys.

        :returns: DataFrame with backtesting results.
        """

        # Initialize the results dataframe
        # to supply to each backtesting process
        results_dataframe = pd.DataFrame()

        # Instantiate the strategy class by typecasting
        # the strategy name from configuration to the corresponding class
        strategy_name = self._configuration.strategy
        strategy_class = type(
            strategy_name,
            (STRATEGY_CATALOGUE_MAP[strategy_name],),
            {},
        )

        # Iterate over each combination of parameters
        for combination in combinations:
            # We copy the dataframe to have a clean
            # set of prices for each combination we are testing
            dataframe_to_test = price_dataframe.copy()

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

            # Append the results of this run to the results dataframe
            if results_dataframe.empty:
                results_dataframe = this_run_results

            else:
                results_dataframe = pd.concat(
                    [results_dataframe, this_run_results],
                )

        return results_dataframe

    def _construct_parameter_combinations(
        self,
        parameter_set: ParameterSet,
    ) -> ParameterKeysAndCombinations:
        """
        Construct parameter sets for each combination of parameters.

        :param parameters: TypedDict with parameter specifications.
        :returns: Tuple with parameter keys and combinations.
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
        return list(parameter_ranges.keys()), product(*parameter_ranges.values())

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
        optimized_parameters: dict[str, Union[str, int, float]],
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
