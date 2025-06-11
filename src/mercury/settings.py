from enum import Enum


class Events(str, Enum):
    """Enum for events used throughout the module."""

    POSITION_OPTIMIZED = "position_optimized"
