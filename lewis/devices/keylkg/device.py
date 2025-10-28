from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .interfaces.stream_interface import Modes
from .states import DefaultState


class SimulatedKeylkg(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.connected = True
        self.input_correct = True

        self.mode = Modes.MEASURE

        self.detector_1_offset = 0.0
        self.detector_2_offset = 0.0
        self.detector_1_raw_value = 0.0
        self.detector_2_raw_value = 0.0

        self.detector_1_measurement_mode = 0
        self.detector_2_measurement_mode = 0

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def reset(self):
        self._initialize_data()
