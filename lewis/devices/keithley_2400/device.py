from __future__ import division

from collections import OrderedDict
from random import uniform

from lewis.devices import StateMachineDevice

from .control_modes import *
from .states import DefaultRunningState, StaticRunningState
from .utilities import format_value


class SimulatedKeithley2400(StateMachineDevice):
    INITIAL_CURRENT = 0.1
    INITIAL_CURRENT_COMPLIANCE = INITIAL_CURRENT
    INITIAL_VOLTAGE = 10.0
    INITIAL_VOLTAGE_COMPLIANCE = INITIAL_VOLTAGE
    MINIMUM_CURRENT = 1.0e-20
    RESISTANCE_RANGE_MULTIPLIER = 2.1

    INITIAL_SOURCE_CURRENT = 1.0e-4
    INITIAL_SOURCE_VOLTAGE = 0.8

    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.random_output = True

        # Power properties
        self.current = SimulatedKeithley2400.INITIAL_CURRENT
        self.voltage = SimulatedKeithley2400.INITIAL_VOLTAGE

        self._source_current = SimulatedKeithley2400.INITIAL_SOURCE_CURRENT
        self._source_voltage = SimulatedKeithley2400.INITIAL_SOURCE_VOLTAGE

        # Modes
        self._output_mode = OutputMode.OFF
        self._offset_compensation_mode = OffsetCompensationMode.OFF
        self._resistance_mode = ResistanceMode.AUTO
        self._remote_sensing_mode = RemoteSensingMode.OFF
        self._resistance_range_mode = ResistanceRangeMode.AUTO

        self._source_mode = SourceMode.CURRENT

        # Ranges

        self._source_current_autorange_mode = AutorangeMode.AUTO
        self._source_voltage_autorange_mode = AutorangeMode.AUTO

        self._source_current_range = SimulatedKeithley2400.INITIAL_CURRENT
        self._source_voltage_range = SimulatedKeithley2400.INITIAL_VOLTAGE

        self._measured_current_autorange_mode = AutorangeMode.AUTO
        self._measured_voltage_autorange_mode = AutorangeMode.AUTO

        self._measured_current_range = SimulatedKeithley2400.INITIAL_CURRENT
        self._measured_voltage_range = SimulatedKeithley2400.INITIAL_VOLTAGE

        # Mode settings
        self._resistance_range = SimulatedKeithley2400.RESISTANCE_RANGE_MULTIPLIER
        self._current_compliance = SimulatedKeithley2400.INITIAL_CURRENT_COMPLIANCE
        self._voltage_compliance = SimulatedKeithley2400.INITIAL_VOLTAGE_COMPLIANCE

    def _get_state_handlers(self):
        return {
            "running": DefaultRunningState(),
            "static": StaticRunningState(),
        }

    def _get_initial_state(self):
        return "static"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("static", "running"), lambda: self.random_output),
                (("running", "static"), lambda: not self.random_output),
            ]
        )

    def _resistance(self):
        # The device only tracks current and voltage. Resistance is calculated as a dependent variable
        r = self.voltage / self.current
        return (
            min(r, self._resistance_range)
            if self._resistance_range_mode == ResistanceRangeMode.MANUAL
            else r
        )

    def _format_power_output(self, value, as_string, offset=0.0):
        """Some properties like output mode and offset compensation affect the output without affecting the underlying
        model. Those adjustments are applied here.
        """
        output_value = value
        if self._offset_compensation_mode == OffsetCompensationMode.ON:
            output_value -= offset
        return format_value(output_value, as_string)

    def set_voltage(self, value):
        self.voltage = value

    def set_current(self, value):
        self.current = value

    def get_voltage(self, as_string=False):
        return self._format_power_output(
            self.voltage, as_string, SimulatedKeithley2400.INITIAL_VOLTAGE
        )

    def get_current(self, as_string=False):
        return self._format_power_output(
            self.current, as_string, SimulatedKeithley2400.INITIAL_CURRENT
        )

    def get_resistance(self, as_string=False):
        return self._format_power_output(self._resistance(), as_string)

    def update(self, dt):
        """Update the current and voltage values based on the current mode and time elapsed."""

        def update_value(value):
            return abs(value + uniform(-1, 1) * dt)

        new_current = max(
            update_value(self.current), SimulatedKeithley2400.MINIMUM_CURRENT
        )
        new_voltage = update_value(self.voltage)

        if self._resistance_mode == ResistanceMode.MANUAL:
            # Restrict the current if we're in current compliance mode. Similarly for voltage
            if (
                new_current < self.current_compliance
                or self._source_mode == SourceMode.VOLTAGE
            ):
                self.current = new_current
            if (
                new_voltage < self._voltage_compliance
                or self._source_mode == SourceMode.CURRENT
            ):
                self.voltage = new_voltage
        elif self._resistance_mode == ResistanceMode.AUTO:
            self.current = new_current
            self.voltage = new_voltage

    def reset(self):
        """Set all the attributes back to their initial values."""
        self._initialize_data()

    @staticmethod
    def _check_mode(mode, mode_class):
        """Make sure the mode requested exists in the related class."""
        if mode in mode_class.MODES:
            return True
        else:
            print(
                "Invalid mode, {}, received for: {}".format(mode, mode_class.__name__)
            )
            return False

    def set_output_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, OutputMode):
            self._output_mode = mode

    def get_output_mode(self):
        return self._output_mode

    def set_offset_compensation_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, OffsetCompensationMode):
            self._offset_compensation_mode = mode

    def get_offset_compensation_mode(self):
        return self._offset_compensation_mode

    def set_resistance_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, ResistanceMode):
            self._resistance_mode = mode

    def get_resistance_mode(self):
        return self._resistance_mode

    def set_remote_sensing_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, RemoteSensingMode):
            self._remote_sensing_mode = mode
            # Output switched off when remote sensing mode changed
            self._output_mode = OutputMode.OFF

    def get_remote_sensing_mode(self):
        return self._remote_sensing_mode

    def set_resistance_range_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, ResistanceRangeMode):
            self._resistance_range_mode = mode

    def get_resistance_range_mode(self):
        return self._resistance_range_mode

    def set_source_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, SourceMode):
            self._source_mode = mode

    def get_source_mode(self):
        return self._source_mode

    def set_resistance_range(self, value):
        self.log.info("Setting resistance range to {}".format(value))
        from math import pow

        # Set the resistance range to the smallest value of 2.1En the requested
        # value exceeds
        self._resistance_range = SimulatedKeithley2400.RESISTANCE_RANGE_MULTIPLIER
        for r in [
            SimulatedKeithley2400.RESISTANCE_RANGE_MULTIPLIER * pow(10, i)
            for i in range(1, 8)
        ]:
            if value < r:
                self._resistance_range = r / 10
                break
        # Resistance range mode set to manual when range set
        self._resistance_range_mode = ResistanceRangeMode.MANUAL

    def get_resistance_range(self):
        return self._resistance_range

    def set_current_compliance(self, value):
        self._current_compliance = value

    def get_current_compliance(self):
        return self._current_compliance

    def set_voltage_compliance(self, value):
        self._voltage_compliance = value

    def get_voltage_compliance(self):
        return self._voltage_compliance

    def get_source_voltage(self):
        return self._source_voltage

    def set_source_voltage(self, value):
        self._source_voltage = value

    def get_source_current(self):
        return self._source_current

    def set_source_current(self, value):
        self._source_current = value

    def get_source_current_autorange_mode(self):
        return self._source_current_autorange_mode

    def set_source_current_autorange_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, AutorangeMode):
            self._source_current_autorange_mode = mode

    def get_source_voltage_autorange_mode(self):
        return self._source_voltage_autorange_mode

    def set_source_voltage_autorange_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, AutorangeMode):
            self._source_voltage_autorange_mode = mode

    def get_source_current_range(self):
        return self._source_current_range

    def set_source_current_range(self, value):
        self._source_current_range = value

    def get_source_voltage_range(self):
        return self._source_voltage_range

    def set_source_voltage_range(self, value):
        self._source_voltage_range = value

    def set_measured_voltage_autorange_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, AutorangeMode):
            self._measured_voltage_autorange_mode = mode

    def get_measured_voltage_autorange_mode(self):
        return self._measured_voltage_autorange_mode

    def set_measured_current_autorange_mode(self, mode):
        if SimulatedKeithley2400._check_mode(mode, AutorangeMode):
            self._measured_current_autorange_mode = mode

    def get_measured_current_autorange_mode(self):
        return self._measured_current_autorange_mode

    def get_measured_current_range(self):
        return self._measured_current_range

    def set_measured_current_range(self, value):
        self._measured_current_range = value

    def get_measured_voltage_range(self):
        return self._measured_voltage_range

    def set_measured_voltage_range(self, value):
        self._measured_voltage_range = value
