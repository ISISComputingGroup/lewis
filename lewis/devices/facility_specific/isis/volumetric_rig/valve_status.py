class ValveStatus(object):
    """An enumeration of possible valve states. OPEN_AND_DISABLED should never happen."""

    OPEN_AND_ENABLED, CLOSED_AND_ENABLED, OPEN_AND_DISABLED, CLOSED_AND_DISABLED = (
        i for i in range(4)
    )
