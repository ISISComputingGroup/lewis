"""Effectively enumerators for each of the various modes supported by the device. Allows checking for invalid mode
strings and helps avoid typos.
"""


class Mode(object):
    MODES = []


class ResistanceRangeMode(Mode):
    AUTO = "1"
    MANUAL = "0"
    MODES = [AUTO, MANUAL]


class AutorangeMode(Mode):
    AUTO = "1"
    MANUAL = "0"
    MODES = [AUTO, MANUAL]


class SourceMode(Mode):
    CURRENT = "CURR"
    VOLTAGE = "VOLT"
    MODES = [CURRENT, VOLTAGE]


class AutoMode(Mode):
    AUTO = "AUTO"
    MANUAL = "MAN"
    MODES = [AUTO, MANUAL]


class ResistanceMode(AutoMode):
    pass


class OnOffMode(Mode):
    ON = "1"
    OFF = "0"
    MODES = [ON, OFF]


class RemoteSensingMode(OnOffMode):
    pass


class OffsetCompensationMode(OnOffMode):
    pass


class OutputMode(OnOffMode):
    pass
