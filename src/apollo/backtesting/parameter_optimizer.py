from itertools import product
from logging import getLogger
from multiprocessing import Pool, cpu_count
from sys import exit

import pandas as pd
from numpy import arange

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.backtesting.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.settings import (
    BACKTESTING_CASH_SIZE,
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    NO_SIGNAL,
    START_DATE,
    STRATEGY,
    TICKER,
)
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
    Writes backtesting results into the database.

    Is multiprocessing capable and runs in parallel.
    """

    def __init__(self) -> None:
        """
        Construct Parameter Optimizer.

        Instantiate configuration that parses strategy parameters file.
        Instantiate database connector that writes backtesting results into database.
        """

        self._configuration = Configuration()
        self._database_connector = PostgresConnector()

    def process_in_parallel(self) -> None:
        """Run the optimization process in parallel."""

        # Instantiate the API connector
        api_connector = YahooApiConnector(
            ticker=str(TICKER),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
            frequency=str(FREQUENCY),
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

            # Output the results to the database
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
        strategy_name = str(STRATEGY)
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
                lot_size_cash=BACKTESTING_CASH_SIZE,
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
            this_run_results["parameters"] = str(combination_to_test)

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
        Prepare and write the backtesting results to the database.

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

        # Extract the best performing parameters
        # as JSON string and prepare them for writing to a file
        optimized_parameters = results_dataframe.iloc[0]["parameters"]
        optimized_parameters = str(optimized_parameters).replace("'", '"')

        # Extract single backtesting results series to write
        backtesting_results = results_dataframe.iloc[0]

        # Write the results to the database
        self._database_connector.write_backtesting_results(
            ticker=str(TICKER),
            strategy=str(STRATEGY),
            frequency=str(FREQUENCY),
            max_period=bool(MAX_PERIOD),
            parameters=optimized_parameters,
            backtesting_results=backtesting_results,
            backtesting_end_date=str(END_DATE),
            backtesting_start_date=str(START_DATE),
        )
