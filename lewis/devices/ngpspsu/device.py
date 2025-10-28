from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedNgpspsu(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self._model_no_and_firmware = "NGPS 100-50:0.9.01"
        self._voltage = 0.0
        self._voltage_setpoint = 0.0
        self._current = 0.0
        self._current_setpoint = 0.0
        self._connected = True
        self._status = {
            "ON/OFF": False,
            "Fault condition": False,
            "Control mode": "Remote",
            "Regulation mode": False,
            "Update mode": "Normal",
            "Ramping": False,
            "Waveform": False,
            "OVT": False,
            "Mains fault": False,
            "Earth leakage": False,
            "Earth fuse": False,
            "Regulation fault": False,
            "Ext. interlock #1": False,
            "Ext. interlock #2": False,
            "Ext. interlock #3": False,
            "Ext. interlock #4": False,
            "DCCT fault": False,
            "OVP": False,
        }

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    @property
    def model_number_and_firmware(self):
        """Returns the model number and firmware version."""
        return self._model_no_and_firmware

    @property
    def status(self):
        """Returns the status of the device."""
        return self._status

    @property
    def voltage(self):
        """Returns voltage to 6 decimal places."""
        return "{0:.6f}".format(self._voltage)

    @property
    def voltage_setpoint(self):
        """Returns last voltage setpoint to 6 decimal places."""
        return "{0:.6f}".format(self._voltage_setpoint)

    def try_setting_voltage_setpoint(self, value):
        """Sets the voltage setpoint.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code.).
        """
        if not self._status["ON/OFF"]:
            return "#NAK:13"
        else:
            value = float(value)
            self._voltage_setpoint = value
            self._voltage = value
            return "#AK"

    @property
    def current(self):
        """Returns current to 6 decimal places."""
        return "{0:.6f}".format(self._current)

    @property
    def current_setpoint(self):
        """Returns current setpoint to 6 decimal places."""
        return "{0:.6f}".format(self._current_setpoint)

    def try_setting_current_setpoint(self, value):
        """Sets the current setpoint.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code).
        """
        if not self._status["ON/OFF"]:
            return "#NAK:13"
        else:
            value = float(value)
            self._current_setpoint = value
            self._current = value
            return "#AK"

    def start_device(self):
        """Starts the device.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code).
        """
        if self._status["ON/OFF"]:
            return "#NAK:09"
        else:
            self._status["ON/OFF"] = True
            return "#AK"

    def stop_device(self):
        """Stops the device.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code).
        """
        if not self._status["ON/OFF"]:
            return "#NAK:13"
        else:
            self._status["ON/OFF"] = False
            self._voltage = 0.00000
            self._current = 0.00000
            return "#AK"

    def reset_device(self):
        """Resets the device.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code).
        """
        for key in self._status:
            if key == "Control mode":
                self._status[key] = "Remote"
            elif key == "Update mode":
                self._status[key] = "Normal"
            else:
                self._status[key] = False

        self._voltage = 0
        self._voltage_setpoint = 0
        self._current = 0
        self._current_setpoint = 0
        return "#AK"

    @property
    def connected(self):
        """Connected status of the device.

        Returns:
            True if the device is connected. False otherwise.
        """
        return self._connected

    def connect(self):
        """Connects the device."""
        self._connected = True

    def disconnect(self):
        """Disconnects the device."""
        self._connected = False

    def fault(self, fault_name):
        """Sets the status depending on the fault. Set only via the backdoor.

        Raises:
            ValueError if fault_name is not a recognised fault.
        """
        if fault_name in self._status:
            self._status[fault_name] = True
        else:
            raise ValueError("Could not find {}".format(fault_name))
