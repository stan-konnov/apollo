from multiprocessing import cpu_count
from typing import Any, Iterable


class Multiprocessor:
    """
    Base class for multiprocessing tasks.

    Contains common attributes for child classes
    and batching logic necessary for parallel processing.
    """

    def __init__(self) -> None:
        """Construct Multiprocessor."""

        # Resolve batch count
        # to number of available cores
        self._batch_count = cpu_count()

    def process_in_parallel(self) -> None:
        """
        Process the task in parallel.

        Is required to be implemented by child classes.
        """

        raise NotImplementedError("Method process_in_parallel is not implemented.")

    def _batch_collection(self, collection: Iterable[Any]) -> list[list[Any]]:
        """
        Split collection into equal batches.

        :param collection: Collection to split into batches.
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
        base_batch_size = items_count // self._batch_count

        # Calculate the size of the remainder batch
        remainder_batch_size = items_count % self._batch_count

        start_index = 0
        batches_to_return = []

        # Iterate over the number of batches
        for i in range(self._batch_count):
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
