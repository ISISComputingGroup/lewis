from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedMezflipr(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.connected = True

        self.powered_on = False
        self.compensation = 0

        self.params = ""
        self.mode = "static"

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
