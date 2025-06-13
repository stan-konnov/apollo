from multiprocessing import cpu_count

from apollo.utils.multiprocessing_capable import MultiprocessingCapable


def test__multiprocessing_capable__for_correct_number_of_cpu_cores() -> None:
    """
    Test Multiprocessing Capable for correctly fetching the number of CPU cores.

    Class must resolve to maximum number of CPU cores available for the system.
    """

    available_cores = cpu_count()

    multiprocessing_capable = MultiprocessingCapable()

    assert multiprocessing_capable._available_cores == available_cores  # noqa: SLF001


def test__create_batches__for_correct_inputs_batching() -> None:
    """
    Test create_batches method for correct inputs batching.

    create_batches() must return list of equally batched inputs.
    """

    multiprocessing_capable = MultiprocessingCapable()

    range_min = 1.0
    range_max = 2.0

    combinations = [
        (range_min, range_min),
        (range_min, range_max),
        (range_max, range_min),
        (range_max, range_max),
    ]

    control_batches = [
        [(range_min, range_min), (range_min, range_max)],
        [(range_max, range_min), (range_max, range_max)],
    ]

    multiprocessing_capable._available_cores = len(control_batches)  # noqa: SLF001
    batches = multiprocessing_capable._create_batches(  # noqa: SLF001
        combinations,
    )

    assert control_batches == batches
