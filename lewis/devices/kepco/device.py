from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedKepco(StateMachineDevice):
    """Simulated Kepco"""

    def _initialize_data(self):
        """Sets the initial state of the device."""
        self.reset_count = 0
        self._idn_no_firmware = "KEPCO,BOP 50-20,E1234,"
        self._firmware = 2.6
        self._init_data()

    def _init_data(self):
        """Initialise device data."""
        self.voltage_set_count = 0
        self.current_set_count = 0
        self._voltage = 10.0
        self._current = 10.0
        self._setpoint_voltage = 10.0
        self._setpoint_current = 10.0
        self.output_mode_set_count = 0
        self.output_status_set_count = 0
        self._output_mode = 0
        self._output_status = 0
        self.connected = True
        self.auto_voltage_range = 1
        self.auto_current_range = 1
        self._voltage_range = 1
        self._current_range = 1

        self.remote_comms_enabled = True

    def reset(self):
        """Reset the device, reinitialising the data.
        :return:
        """
        self.reset_count += 1
        self._init_data()

    def _get_state_handlers(self):
        """Returns: states and their names"""
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """Returns: the name of the initial state"""
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions"""
        return OrderedDict()

    @property
    def idn(self):
        """:return: IDN- Identification String"""
        return self._idn_no_firmware + str(self._firmware)

    @property
    def idn_no_firmware(self):
        """:return: IDN- Identification String"""
        return self._idn_no_firmware

    @idn_no_firmware.setter
    def idn_no_firmware(self, idn_no_firmware):
        """:param idn_no_firmware:
        :return: sets IDN without the firmware- Identification String
        """
        self._idn_no_firmware = idn_no_firmware

    @property
    def firmware(self):
        """:return: IDN- Identification String"""
        return self._firmware

    @firmware.setter
    def firmware(self, firmware):
        """:param firmware:
        :return: sets the firmware of the device (part of the IDN)
        """
        self._firmware = firmware

    @property
    def voltage(self):
        """Returns: the Voltage"""
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        """:param voltage: Write the Voltage"""
        self._voltage = voltage

    @property
    def current(self):
        """:return: get the Current"""
        return self._current

    @current.setter
    def current(self, current):
        """:param write the current:"""
        self._current = current

    @property
    def setpoint_voltage(self):
        """Returns: the Setpoint Voltage"""
        return self._setpoint_voltage

    @setpoint_voltage.setter
    def setpoint_voltage(self, setpoint_voltage):
        """:param setpoint_voltage: set the Setpoint Voltage
        :return:
        """
        self.voltage_set_count += 1
        self._setpoint_voltage = setpoint_voltage

    @property
    def setpoint_current(self):
        """Returns: the Setpoint Current"""
        return self._setpoint_current

    @setpoint_current.setter
    def setpoint_current(self, setpoint_current):
        """:param setpoint_current: set the setpoint current
        :return:
        """
        self.current_set_count += 1
        self._setpoint_current = setpoint_current

    @property
    def output_mode(self):
        """:return:  Returns the output mode"""
        return self._output_mode

    @output_mode.setter
    def output_mode(self, mode):
        """:param mode: Set output mode"""
        self.output_mode_set_count += 1
        self._output_mode = mode

    @property
    def output_status(self):
        """:return: Output status"""
        return self._output_status

    @output_status.setter
    def output_status(self, status):
        """:param status: set Output status"""
        self.output_status_set_count += 1
        self._output_status = status

    @property
    def voltage_range(self):
        """Returns: the Voltage range"""
        return self._voltage_range

    @voltage_range.setter
    def voltage_range(self, range):
        """:param range: the Voltage range"""
        self._voltage_range = range
        self.auto_voltage_range = 0

    @property
    def current_range(self):
        """Returns: the Currrent range"""
        return self._current_range

    @current_range.setter
    def current_range(self, range):
        """:param range: the Current range"""
        self._current_range = range
        self.auto_current_range = 0
