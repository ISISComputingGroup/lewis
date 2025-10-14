from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedMecfrf(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.sensor1 = 123
        self.sensor2 = 456

        self.corrupted_messages = False
        self.connected = True

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def reset(self):
        self._initialize_data()

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
