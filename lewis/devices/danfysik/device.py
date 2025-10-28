from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class FieldUnits(object):
    """Field units."""

    OERSTED = object()
    GAUSS = object()
    TESLA = object()


class SimulatedDanfysik(StateMachineDevice):
    """Simulated Danfysik."""

    def _initialize_data(self):
        """Sets the initial state of the device."""
        self.comms_initialized = False
        self.connected = True

        self.field = 0
        self.field_sp = 0

        self.absolute_current = 0
        self.voltage = 0
        self.voltage_read_factor = 1
        self.current_read_factor = 1
        self.current_write_factor = 1

        # DAC 1, DAC 2, DAC 1 absolute slew rates
        self.slew_rate = [0, 0, 0]

        self.field_units = FieldUnits.GAUSS
        self.negative_polarity = False
        self.power = True

        # Use a list of active interlocks because each danfysik has different sets of interlocks which can be enabled.
        self.active_interlocks = []

        self.currently_addressed_psu = 0
        self.address = 75

    def enable_interlock(self, name):
        """Adds an interlock to the list of enabled interlock
        Args:
            name: the name of the interlock to enable.
        """
        if name not in self.active_interlocks:
            self.active_interlocks.append(name)

    def disable_interlock(self, name):
        """Removes an interlock from the list of enabled interlocks
        Args:
            name: the name of the interlock to disable.
        """
        if name in self.active_interlocks:
            self.active_interlocks.remove(name)

    def set_address(self, value):
        """Changes the currently addressed PSU

        Args:
            value: int, the address to set the PSU to.
        """
        self.currently_addressed_psu = value

        self.log.info("Address set to, {}".format(value))

        if self.address != self.currently_addressed_psu:
            self.comms_initialized = False
            self.log.info("Device down")
        else:
            self.comms_initialized = True
            self.log.info("Device up")

    def reset(self):
        """Reset the device to the standard off configuration."""
        self.absolute_current = 0
        self.voltage = 0
        self.power = False

    def reinitialise(self):
        """Reinitialise the device state (this is mainly used via the backdoor to clean up between tests)"""
        self._initialize_data()

    def set_current_read_factor(self, factor):
        """Set the scale factor between current and raw when reading a value.

        Args:
            factor: The scale factor to apply.
        """
        self.current_read_factor = factor

    def set_current_write_factor(self, factor):
        """Set the scale factor between current and raw when writing a value.

        Args:
            factor: The scale factor to apply.
        """
        self.current_write_factor = factor

    def get_current(self):
        """Return:
        The readback value of current as raw value (parts per 100,000)
        """
        raw_rbv = self.absolute_current / self.current_read_factor
        return raw_rbv

    def get_last_setpoint(self):
        """Return:
        The setpoint readback value of current as raw value (parts per 1,000,000)
        """
        raw_sp_rbv = self.absolute_current * self.current_write_factor
        return raw_sp_rbv

    def set_current(self, raw_sp):
        """Set a new value for current.

        Args:
            raw_sp: The new value in raw (parts per 1,000,000)
        """
        current = raw_sp / self.current_write_factor
        self.absolute_current = abs(current)
        self.negative_polarity = current < 0

    def get_voltage(self):
        """Return:
        The readback value of voltage scaled by the custom scale factor
        """
        return self.voltage * self.voltage_read_factor

    def set_slew_rate(self, dac_num, value):
        self.slew_rate[dac_num - 1] = value

    def get_slew_rate(self, dac_num):
        return self.slew_rate[dac_num - 1]

    def _get_state_handlers(self):
        """Returns: states and their names"""
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """Returns: the name of the initial state"""
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions"""
        return OrderedDict()
