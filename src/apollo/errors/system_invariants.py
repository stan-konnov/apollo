class ScreenedPositionAlreadyExistsError(Exception):
    """Raised before the screening process if screened position exists."""


class OptimizedPositionAlreadyExistsError(Exception):
    """Raised before the optimization process if optimized position exists."""


class DispatchedPositionAlreadyExistsError(Exception):
    """Raised before the dispatching process if dispatched position exists."""


class NeitherOpenNorOptimizedPositionExistsError(Exception):
    """Raised if neither open nor optimized position exists during dispatching."""


class OpenPositionAlreadyExistsError(Exception):
    """Raised if an open position already exists during order execution."""


class DispatchedPositionDoesNotExistError(Exception):
    """Raised if dispatched position does not exist during order execution."""
