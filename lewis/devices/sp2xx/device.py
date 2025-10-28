"""Items associated with WPI SP2XX syringe pump"""

from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState
from .util_classes import ErrorType, RunStatus
from .util_constants import DIRECTIONS, MODES, NO_ERROR


class SimulatedSp2XX(StateMachineDevice):
    """Simulation of the WPI SP2XX syringe pump"""

    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self._running_status = RunStatus.Stopped
        self._direction = DIRECTIONS["I"]
        self._running = False
        self._last_error = NO_ERROR
        self._mode = MODES["i"]
        self._diameter = 0.0
        self.connect()
        self.infusion_volume_units = "ml"
        self.infusion_volume = 12.0
        self.withdrawal_volume_units = "ml"
        self.withdrawal_volume = 12.0
        self.infusion_rate_units = "ml/m"
        self.infusion_rate = 12.0
        self.withdrawal_rate_units = "ml/m"
        self.withdrawal_rate = 12.0

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    @property
    def running(self):
        """Returns True if the device is running and False otherwise."""
        return self._running

    @property
    def direction(self):
        """Returns the direction the pump is set to."""
        return self._direction

    def set_direction_via_the_backdoor(self, direction_symbol):
        """Sets the direction via the backdoor. Only called using lewis via the backdoor.

        Args:
            direction_symbol: Infusion or Withdrawal.

        Returns:
            None
        """
        self._direction = DIRECTIONS[direction_symbol]

    def reverse_direction(self):
        """Reverses the direction of the device and change mode and status accordingly. But only if it is in
        Infusion or withdrawal mode and running. Other reverse can not be sent.

        Returns:
            True if direction was reversed; False otherwise
        """
        # it is not clear whether the actual device sets the mode on reverse or not; and it it not important
        # enough to find out
        if self.mode.response == "I" and self._running:
            self.set_mode("w")
            self._running_status = RunStatus.Withdrawal
            did_reverse = True
        elif self.mode.response == "W" and self._running:
            self.set_mode("i")
            self._running_status = RunStatus.Infusion
            did_reverse = True
        else:
            did_reverse = False
        return did_reverse

    def start_device(self):
        """Starts the device running to present settings.

        Returns:
            None
        """
        self._running = True
        self._running_status = RunStatus[self._direction.name]

    def stop_device(self):
        """Stops the device running.

        Returns:
            None
        """
        self._running = False
        self._running_status = RunStatus.Stopped

    @property
    def running_status(self):
        """Returns the running status of the device."""
        return self._running_status

    @property
    def mode(self):
        """Returns the mode the device is in.

        Returns:
            _mode: Mode class that the device is in.
        """
        return self._mode

    def set_mode(self, mode_symbol):
        """Sets the mode of the device.

        Args:
            mode_symbol: one of i, w, w/i, i/w, con.

        Returns:
            None
        """
        if mode_symbol in ["i", "i/w", "con"]:
            self._direction = DIRECTIONS["I"]
        elif mode_symbol in ["w", "w/i"]:
            self._direction = DIRECTIONS["W"]
        else:
            print("Could not set direction.")

        self._mode = MODES[mode_symbol]

    @property
    def last_error(self):
        """Returns the last error type."""
        return self._last_error

    def throw_error_via_the_backdoor(self, error_name, error_value, error_alarm_severity):
        """Throws an error of type error_type. Set only via the backdoor

        Args:
            error_name: Name of the error to throw.
            error_value: Integer value of error.
            error_alarm_severity: Alarm severity.

        Returns:
            "\r\nE": Device error prompt.
        """
        new_error = ErrorType(error_name, error_value, error_alarm_severity)
        self._last_error = new_error

    def clear_last_error(self):
        """Clears the last error.

        Returns:
            None.
        """
        self._last_error = NO_ERROR

    @property
    def diameter(self):
        """Returns: the diameter of the syringe set on the device"""
        return self._diameter

    def successfully_set_diameter(self, value):
        """Sets the diameter after checking the input value. Must be in the form nn.nn.

        Returns:
            True if the diameter has been set and False otherwise.
        """
        if value >= 100 or value < 0.01:
            return False
        else:
            value = round(value, 2)
            self._diameter = value
            return True

    @property
    def connected(self):
        """Returns True if the device is connected and False if disconnected."""
        return self._connected

    def connect(self):
        """Connects the device.

        Returns:
            None
        """
        self._connected = True

    def discconnect(self):
        """Disconnects the device.

        Returns:
            None
        """
        self._connected = False
