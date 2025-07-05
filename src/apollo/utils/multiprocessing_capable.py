from collections.abc import Iterable
from multiprocessing import cpu_count
from typing import TypeVar

# Declare a generic type for inputs
# collection item since different tasks
# operate on different types of data structures
TItem = TypeVar("TItem")


class MultiprocessingCapable:
    """
    Base class for multiprocessing tasks.

    Contains common attributes for child classes
    and batching logic necessary for parallel processing.
    """

    def __init__(self) -> None:
        """Construct Multiprocessing Capable class."""

        # Get number of available cores
        self._available_cores = cpu_count()

    def _create_batches(self, inputs: Iterable[TItem]) -> list[list[TItem]]:
        """
        Break inputs collection into equal batches.

        :param inputs: Inputs collection to batch.
        :returns: List of batches with collection items.
        """

        # Map inputs to list if it is not one already
        inputs = list(inputs) if not isinstance(inputs, list) else inputs

        # Calculate the
        # total number of items
        items_count = len(inputs)

        # Calculate the base size of each batch
        base_batch_size = items_count // self._available_cores

        # Calculate the size of the remainder batch
        remainder_batch_size = items_count % self._available_cores

        start_index = 0
        batches_to_return = []

        # Iterate over the number of batches
        for i in range(self._available_cores):
            # Calculate the current batch size
            current_batch_size = base_batch_size + (
                1 if i < remainder_batch_size else 0
            )

            # Slice and append the current batch
            batches_to_return.append(
                inputs[start_index : start_index + current_batch_size],
            )

            # Update the start index for the next batch
            start_index += current_batch_size

        return batches_to_return
