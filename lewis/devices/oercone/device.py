from collections import OrderedDict
from enum import Enum, unique

from lewis.devices import StateMachineDevice

from .states import DefaultState


@unique
class Units(Enum):
    mbar = 0
    Torr = 1
    Pascal = 2
    Micron = 3


@unique
class ReadState(Enum):
    PR1 = 0
    UNI = 1


class SimulatedOercone(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self._pressure = 0
        self._measurement_unit = Units.mbar
        self._read_state = None

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    @property
    def pressure(self):
        """Returns the value of the pressure sensor.

        Returns:
            float: Pressure value.
        """
        return self._pressure

    @pressure.setter
    def pressure(self, pressure):
        """Sets the pressure sensor.

        Args:
            pressure: Value to set pressure sensor to.

        Returns:
            None
        """
        self._pressure = pressure

    @property
    def measurement_unit(self):
        """Returns the value of the pressure sensor.

        Returns:
            Units: The enum unit currently in use e.g. Units.Micron.
        """
        return self._measurement_unit

    @measurement_unit.setter
    def measurement_unit(self, units):
        """Sets the curent units.

        Args:
            units (Units member): Enum value to set the units to.

        Returns:
            None
        """
        self._measurement_unit = units

    def backdoor_set_units(self, unit):
        """Sets unit on device. Called only via the backdoor using lewis.

        Args:
            unit: integer 0, 1, 2, or 3

        Returns:
            None
        """
        self.measurement_unit = Units(int(unit))

    @property
    def read_state(self):
        """Returns the readstate for the device

        Returns:
            Enum: Readstate of the device.
        """
        return self._read_state

    @read_state.setter
    def read_state(self, state):
        """Sets the readstate of the device

        Args:
            state: Enum readstate of the device to be set

        Returns:
            None
        """
        self._read_state = state
