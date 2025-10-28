from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedFlipprps(StateMachineDevice):
    def _initialize_data(self):
        DOWN = 0
        self.polarity = DOWN
        self.id = "Flipper"
        self.connected = True

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
