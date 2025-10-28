from collections import OrderedDict

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import DefaultState


class Sensor(object):
    def __init__(self):
        self.setpoint = 0

        self.valve_enabled = False
        self.relay_enabled = False

        self.gain = 0
        self.offset = 0
        self.rtd_offset = 0
        self.input_range = 0
        self.output_range = 0
        self.ext_input_range = 0
        self.ext_output_range = 0
        self.scale = 0
        self.upper_limit = 0
        self.lower_limit = 0

        self.signalmode = 0
        self.limitmode = 0

        self.formula_relay = "formula+1"

        self.external_input = 0

        self.range = 0
        self.range_units = 0


@has_log
class Simulated_MKS_PR4000B(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.channels = {
            1: Sensor(),
            2: Sensor(),
        }
        self.connected = True
        self.remote_mode = True

    def reset(self):
        self._initialize_data()

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def backdoor_set_channel_property(self, channel, property, value):
        setattr(self.channels[int(channel)], str(property), float(value))
