from enum import Enum

from lewis.core import approaches
from lewis.core.statemachine import State


class WarnStateCode(Enum):
    STATIONARY = 256
    MOVING = 512
    UNDEFINED_POSITION = 768


class ErrorStateCode(Enum):
    NONE = 0
    ERROR = 1


class StoppedState(State):
    def on_entry(self, dt):
        device = self._context
        self.log.info("Entering STOPPED state")
        device.motor_warn_status = WarnStateCode.STATIONARY

    def in_state(self, dt):
        device = self._context
        if not device.within_hard_limits():
            device.motor_warn_status = WarnStateCode.UNDEFINED_POSITION


class MovingState(State):
    def on_entry(self, dt):
        device = self._context
        self.log.info("Entering MOVING state")
        device.motor_warn_status = WarnStateCode.MOVING

    def in_state(self, dt):
        device = self._context
        device.position = approaches.linear(
            device.position, device.target_position, device.velocity, dt
        )
        if (
            not device.within_hard_limits()
        ):  # If outside of limits device controller faults and must be re-initialised
            device.motor_warn_status = WarnStateCode.UNDEFINED_POSITION
        if abs(device.target_position - device.position) <= device.tolerance:
            device.position_reached = True
