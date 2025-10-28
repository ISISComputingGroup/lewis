from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class Channel(object):
    def __init__(self):
        self.field_reading = 1.234
        self.field_multiplier = " "
        self.max_hold_reading = 0
        self.max_hold_multiplier = " "
        self.rel_mode_reading = 0.5645
        self.rel_mode_multiplier = " "
        self.mode = 0
        self.prms = 0
        self.filter_status = 0
        self.rel_mode_status = 0
        self.auto_mode_status = 0
        self.max_hold_status = 0
        self.channel_status = 0
        self.filter_windows = 5
        self.filter_points = 32
        self.manual_range = 1
        self.relative_setpoint = 1.123
        self.relative_setpoint_multiplier = "u"


class SimulatedLakeshore460(StateMachineDevice):
    """Simulated Lakeshore 460"""

    def _initialize_data(self):
        """Sets the initial state of the device."""
        self.idn = "LSCI,MODEL460,0,22323"
        self.source = 1
        self.channels = {"X": Channel(), "Y": Channel(), "Z": Channel(), "V": Channel()}
        self.channel = "X"
        self.unit = "T"

    def _get_state_handlers(self):
        """Returns: states and their names"""
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """Returns: the name of the initial state"""
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions"""
        return OrderedDict()

    # This is a workaround for https://github.com/DMSC-Instrument-Data/lewis/issues/248
    def set_channel_param(self, channel, param, value):
        setattr(self.channels[str(channel)], str(param), value)

    # This is a workaround for https://github.com/DMSC-Instrument-Data/lewis/issues/248
    def get_channel_param(self, channel, param):
        return getattr(self.channels[str(channel)], str(param))

    def update_reading_and_multiplier(self, reading, multiplier):
        """Args:
            reading: A reading from the device.
            multiplier: The current multiplier for the reading.

        Returns:
            new_reading: Updated reading value, based on more appropriate multiplier
            new_multiplier: updated multiplier for the value
        """
        stripped_reading = self.strip_multiplier(reading, multiplier)
        new_multiplier = self.calculate_multiplier(stripped_reading)
        new_reading = self.apply_multiplier(stripped_reading, new_multiplier)
        return new_reading, new_multiplier

    def strip_multiplier(self, reading, multiplier):
        """Args:
            reading: A reading from the device with multiplier applied.
            multiplier: The current multiplier for the reading.

        Returns:
                The raw reading.
        """
        if multiplier == "u":
            return reading * 0.000001
        if multiplier == "m":
            return reading * 0.001
        if multiplier == "k":
            return reading * 1000
        else:
            return reading

    def apply_multiplier(self, reading, multiplier):
        """Args:
            reading:  A raw reading from the device.
            multiplier: The multiplier to be applied.

        Returns:
            The reading with the multiplier applied.
        """
        if multiplier == "u":
            return reading / 0.000001
        if multiplier == "m":
            return reading / 0.001
        if multiplier == "k":
            return reading / 1000
        else:
            return reading

    def convert_units(self, convert_value):
        """Converts between Tesla and Gauss (applies conversion of *10000 or *0.0001)
        Then updates reading values according to the more appropriate multiplier

        Args:
            convert_value: 10000 (converting to gauss) or 0.0001 (to Tesla).

        Returns:
            None.
        """
        channels = ["X", "Y", "Z", "V"]
        for c in channels:
            self.channel = c
            self.channels[c].field_reading *= convert_value
            self.channels[c].field_reading, self.channels[c].field_multiplier = (
                self.update_reading_and_multiplier(
                    self.channels[c].field_reading, self.channels[c].field_multiplier
                )
            )
            self.channels[c].max_hold_reading *= convert_value
            self.channels[c].max_hold_reading, self.channels[c].max_hold_multiplier = (
                self.update_reading_and_multiplier(
                    self.channels[c].max_hold_reading, self.channels[c].max_hold_multiplier
                )
            )
            self.channels[c].rel_mode_reading *= convert_value
            self.channels[c].rel_mode_reading, self.channels[c].rel_mode_multiplier = (
                self.update_reading_and_multiplier(
                    self.channels[c].rel_mode_reading, self.channels[c].rel_mode_multiplier
                )
            )
            self.channels[c].relative_setpoint *= convert_value
            self.channels[c].relative_setpoint, self.channels[c].relative_setpoint_multiplier = (
                self.update_reading_and_multiplier(
                    self.channels[c].relative_setpoint,
                    self.channels[c].relative_setpoint_multiplier,
                )
            )

    def calculate_multiplier(self, reading):
        """Calculates the most appropriate multiplier for a given value.

        Args:
            reading: A raw reading from the device.

        Returns:
            The most appropriate multiplier value for the given raw reading.

        """
        if reading <= 0.001:
            return "u"
        if 0.001 < reading <= 0:
            return "m"
        if 0 < reading < 1000:
            return " "
        else:
            return "k"
