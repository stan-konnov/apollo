class ScreenedPositionAlreadyExistsError(Exception):
    """Raised before the screening process if screened position exists."""


class OptimizedPositionAlreadyExistsError(Exception):
    """Raised before the optimization process if optimized position exists."""


class DispatchedPositionAlreadyExistsError(Exception):
    """Raised before the dispatching process if dispatched position exists."""
