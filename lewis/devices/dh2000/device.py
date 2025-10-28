from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedDh2000(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self._shutter_is_open = False
        self._interlock_triggered = False
        self.is_connected = True

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    @property
    def shutter_is_open(self):
        """Returns whether the shutter is open or closed

        Returns:
            shutter_is_open: Bool, True if the shutter is open

        """
        return self._shutter_is_open

    @shutter_is_open.setter
    def shutter_is_open(self, value):
        """Sets whether the shutter is open or closed
        Args:
            value: Boolean, set to True to open the shutter

        Returns:
            None
        """
        self._shutter_is_open = value

    @property
    def interlock_is_triggered(self):
        """Returns whether the interlock has been triggered

        Returns:
            interlock_is_triggered: Bool, True if the interlock has been triggered (forcing shutter closed)

        """
        return self._interlock_triggered

    @interlock_is_triggered.setter
    def interlock_is_triggered(self, value):
        """Sets the interlock triggered status

        Returns:
            None

        """
        self._interlock_triggered = value
