class ActivePositionAlreadyExistsError(Exception):
    """
    Raised when attempting to create new position while active position exists.

    NOTE: We consider a position to be active if it
    falls under any of the following statuses:
    screened, backtested, dispatched, open.
    """
