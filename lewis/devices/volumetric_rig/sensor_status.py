class SensorStatus(object):
    """An enumeration of possible sensor states.
    """

    UNKNOWN, DISABLED, NO_REPLY, VALUE_IN_RANGE, VALUE_TOO_LOW, VALUE_TOO_HIGH = (
        i for i in range(6)
    )
