from collections import OrderedDict

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import DefaultState


@has_log
class SimulatedItc503(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.p, self.i, self.d = 0, 0, 0
        self.gas_flow = 0
        self.temperature = 0
        self.temperature_sp = 0
        self.mode = 0
        self.control = 0
        self.sweeping = False
        self.control_channel = 1
        self.autopid = False

        self.heater_v = 0

        # Set by tests, affects the response format of the device. Slightly different models of ITC will respond
        # differently
        self.report_sweep_state_with_leading_zero = False

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
