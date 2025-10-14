from enum import Enum


class RunStatus(Enum):
    Stopped = 0
    Infusion = 1
    Withdrawal = 2


class Direction(object):
    """Attributes:
    symbol: Respinse symbol, I or W.
    name: Name of the direction. Infusion of withdrawal.
    """

    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name


class Mode(object):
    """Operation mode for the device.

    Attributes:
        set_symbol (string): Symbol for setting the mode
        response (string): Response to a query for the mode.
        name: Description of the mode.
    """

    def __init__(self, symbol, response, name):
        self.symbol = symbol
        self.response = response
        self.name = name


class ErrorType(object):
    """Error Type.

    Attributes:
        name: String name of the error
        value: integer value of the error
        alarm_severity: Alarm severity of the error
    """

    def __init__(self, name, value, alarm_severity):
        self.name = name
        self.value = value
        self.alarm_severity = alarm_severity
