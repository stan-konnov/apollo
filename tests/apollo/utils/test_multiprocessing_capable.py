from multiprocessing import cpu_count

from apollo.utils.multiprocessing_capable import MultiprocessingCapable


def test__multiprocessing_capable__for_correct_number_of_cpu_cores() -> None:
    """
    Test MultiprocessingCapable class for correctly fetching the number of CPU cores.

    Class must resolve to maximum number of CPU cores available for the system.
    """

    available_cores = cpu_count()

    multiprocessing_capable = MultiprocessingCapable()

    assert multiprocessing_capable._available_cores == available_cores  # noqa: SLF001
