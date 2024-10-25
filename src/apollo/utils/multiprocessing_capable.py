from multiprocessing import cpu_count
from typing import Iterable, TypeVar

# Declare a generic type for the
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

    def process_in_parallel(self) -> None:
        """
        Process the task in parallel.

        Is required to be implemented by child classes.
        """

        raise NotImplementedError("Method process_in_parallel is not implemented.")

    def _batch_collection(self, collection: Iterable[TItem]) -> list[list[TItem]]:
        """
        Split collection into equal batches.

        :param collection: Collection to batch.
        :returns: List of batches with collection items.
        """

        # Map collection to list if it is not one already
        collection = (
            list(collection) if not isinstance(collection, list) else collection
        )

        # Calculate the
        # total number of items
        items_count = len(collection)

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
                collection[start_index : start_index + current_batch_size],
            )

            # Update the start index for the next batch
            start_index += current_batch_size

        return batches_to_return
