from itertools import product
from json import dumps
from logging import getLogger
from multiprocessing import Pool
from sys import exit

import pandas as pd
from numpy import arange

from apollo.backtesters.backtesting_runner import BacktestingRunner
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.core.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.errors.system_invariants import OptimizedPositionAlreadyExistsError
from apollo.providers.price_data_enhancer import PriceDataEnhancer
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    BACKTESTING_CASH_SIZE,
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    NO_SIGNAL,
    START_DATE,
    STRATEGY,
    TICKER,
    ParameterOptimizerMode,
)
from apollo.utils.configuration import Configuration
from apollo.utils.multiprocessing_capable import MultiprocessingCapable
from apollo.utils.types import (
    ParameterCombinations,
    ParameterKeysAndCombinations,
    ParameterSet,
)

logger = getLogger(__name__)


class ParameterOptimizer(MultiprocessingCapable):
    """
    Parameter Optimizer class.

    Consumes configuration object with strategy parameters.
    Constructs ranges and combinations of parameters to optimize.
    Runs series of backtesting processes each for each set of parameters.
    Writes highest rated backtesting results and parameters into the database.

    Is multiprocessing capable and runs in parallel.

    TODO: run the whole process on SPY to get time estimate.
    TODO: due to hardware constraints, limit historical data to -30 years.
    """

    def __init__(self, operation_mode: ParameterOptimizerMode) -> None:
        """
        Construct Parameter Optimizer.

        Instantiate Configuration.
        Instantiate Database Connector.
        Instantiate Price Data Provider.
        Instantiate Price Data Enhancer.

        :param operation_mode: Mode of operation.
        """

        super().__init__()

        self._operation_mode = operation_mode

        self._configuration = Configuration()
        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()
        self._price_data_enhancer = PriceDataEnhancer()

    def process_in_parallel(self) -> None:
        """Run the optimization process in parallel."""

        logger.info("Optimization process started.")

        # If we are optimizing over the whole strategy catalogue,
        # it means this process is part of larger signal generation process
        if self._operation_mode == ParameterOptimizerMode.MULTIPLE_STRATEGIES:
            # Query the screened position to optimize
            screened_position = (
                self._database_connector.get_existing_screened_position()
            )

            # Skip the optimization process
            # if the position does not exist
            #
            # This covers low-probability edge case
            # when the screening process produced the
            # same ticker and no position was initialized
            if not screened_position:
                logger.info(
                    "Screened position does not exist. "
                    "Skipping optimization process and proceeding further.",
                )

                return

            # Query the existing optimized position
            existing_optimized_position = (
                self._database_connector.get_existing_optimized_position()
            )

            # Raise an error if the
            # optimized position already exists
            if existing_optimized_position:
                raise OptimizedPositionAlreadyExistsError(
                    "Optimized position for ",
                    f"{existing_optimized_position.ticker} already exists. "
                    "System invariant violated, previous position not dispatched.",
                )

            # Iterate over each strategy in the catalogue
            for strategy in STRATEGY_CATALOGUE_MAP:
                # And optimize each
                self._run_optimization_process(
                    ticker=screened_position.ticker,
                    strategy=strategy,
                )

            # Update the screened position to optimized
            # NOTE: move to separate method and check if optimized position exists
            self._database_connector.update_position_on_optimization(
                screened_position.id,
            )

            logger.info(
                "Optimization process complete. "
                f"Catalogue for {screened_position.ticker} is now optimized.",
            )

        # Otherwise, we are optimizing
        # single strategy for development purposes
        # and we can run the process with default parameters
        if self._operation_mode == ParameterOptimizerMode.SINGLE_STRATEGY:
            self._run_optimization_process()

    def _run_optimization_process(
        self,
        ticker: str = str(TICKER),
        strategy: str = str(STRATEGY),
    ) -> None:
        """
        Run the optimization process for single or multiple strategies.

        :param ticker: Ticker symbol.
        :param strategy: Strategy name.
        """

        # Get parameter set for the strategy
        parameter_set = self._configuration.get_parameter_set(strategy)

        period = "Maximum available" if MAX_PERIOD else f"{START_DATE} - {END_DATE}"
        logger.info(
            f"Running {strategy} for {ticker}\n\n"
            f"Period: {period}\n\n"
            f"Frequency: {FREQUENCY}\n\n"
            "Parameters:\n\n"
            f"{dumps(parameter_set, indent=4)}",
        )

        # Request or read the price data
        price_dataframe = self._price_data_provider.get_price_data(
            ticker=ticker,
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        # Enhance the price data based on the configuration
        price_dataframe = self._price_data_enhancer.enhance_price_data(
            price_dataframe,
            parameter_set["additional_data_enhancers"],
        )

        # Build keys and combinations of parameters to optimize
        keys, combinations = self._construct_parameter_combinations(
            parameter_set,
        )

        # Break down combinations into equal batches
        batches = self._create_batches(combinations)

        # Create arguments to supply to each process
        batch_arguments = [
            (strategy, batch, price_dataframe, parameter_set, keys) for batch in batches
        ]

        # Process each batch in parallel
        with Pool(processes=self._available_cores) as pool:
            # Backtest each batch of parameter combinations
            results = pool.starmap(self._optimize_parameters, batch_arguments)

            # Concatenate the results from each process
            combined_results = pd.concat(results)

            # Output the results to the database
            self._output_results(
                ticker=ticker,
                results_dataframe=combined_results,
            )

    def _optimize_parameters(
        self,
        strategy_name: str,
        combinations: ParameterCombinations,
        price_dataframe: pd.DataFrame,
        parameter_set: ParameterSet,
        keys: list[str],
    ) -> pd.DataFrame:
        """
        Run the optimization process.

        :param strategy_name: Strategy name.
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
            results_dataframe = pd.concat([results_dataframe, this_run_results])

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

    def _output_results(self, ticker: str, results_dataframe: pd.DataFrame) -> None:
        """
        Prepare and write the backtesting results to the database.

        :param ticker: Ticker symbol.
        :param results_dataframe: DataFrame with backtesting results.
        """

        # Sort the results by sharpe ratio, total return, and number of trades
        results_dataframe.sort_values(
            ["Sharpe Ratio", "Return [%]", "# Trades"],
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
            ticker=ticker,
            strategy=str(STRATEGY),
            frequency=str(FREQUENCY),
            max_period=bool(MAX_PERIOD),
            parameters=optimized_parameters,
            backtesting_results=backtesting_results,
            backtesting_end_date=str(END_DATE),
            backtesting_start_date=str(START_DATE),
        )
