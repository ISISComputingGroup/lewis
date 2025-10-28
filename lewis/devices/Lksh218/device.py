from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState

NUMBER_OF_TEMP_CHANNELS = 8
NUMBER_OF_SENSOR_CHANNELS = 8


class SimulatedLakeshore218(StateMachineDevice):
    """Simulated Lakeshore 218
    """

    def _initialize_data(self):
        """Sets the initial state of the device.
        """
        self._temps = [1.0] * NUMBER_OF_TEMP_CHANNELS
        self._sensors = [0.5] * NUMBER_OF_SENSOR_CHANNELS
        self.temp_all = ""
        self.sensor_all = ""
        self.connected = True

    @staticmethod
    def _get_state_handlers():
        """Returns: States and their names.
        """
        return {DefaultState.NAME: DefaultState()}

    @staticmethod
    def _get_initial_state():
        """Returns: The name of the initial state.
        """
        return DefaultState.NAME

    @staticmethod
    def _get_transition_handlers():
        """Returns: The state transitions.
        """
        return OrderedDict()

    def get_temp(self, number):
        """Gets the temperature of a specific temperature sensor.

        Args:
            number: Integer between 1 and 8.

        Returns:
            float: Temperature value at position (number - 1) in temps.
        """
        return self._temps[number - 1]

    def set_temp(self, number, temperature):
        """Sets the (number - 1) temp pv to temperature.

        Args:
            number: Integer between 1 and 8.
            temperature: Temperature reading to set.

        Returns:
            None
        """
        self._temps[number - 1] = temperature

    def get_sensor(self, number):
        """Gets the sensor reading of a specific sensor.

        Args:
            number: Integer between 1 and 8.

        Returns:
            float: Value of sensor at position (number - 1) in sensors.
        """
        return self._sensors[number - 1]

    def set_sensor(self, number, value):
        """Sets the (number - 1) sensor pv to value.

        Args:
            number: Integer between 1 and 8.
            value: Sensor reading to set.

        Returns:
            None
        """
        self._sensors[number - 1] = value
