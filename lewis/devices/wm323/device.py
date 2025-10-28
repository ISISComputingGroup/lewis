from collections import OrderedDict
from enum import Enum

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import DefaultState


class Direction(Enum):
    CCW = 0
    CW = 1


@has_log
class SimulatedWm323(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.speed = 0
        self.direction = Direction.CCW
        self.running = False
        self.type = "323Du"

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
