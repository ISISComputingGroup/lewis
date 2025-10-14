import logging
import typing

from lewis.core import approaches
from lewis.core.logging import has_log
from lewis.core.statemachine import State

if typing.TYPE_CHECKING:
    from .device import SimulatedCRYOSMS


def get_target_value(device: "SimulatedCRYOSMS") -> float:
    if device.ramp_target == "MID":
        target_value = device.mid_target
    elif device.ramp_target == "MAX":
        target_value = device.max_target
    else:
        target_value = 0

    return target_value


class DefaultInitState(State):
    def in_state(self, dt: float) -> None:
        device = typing.cast("SimulatedCRYOSMS", self._context)
        device.check_is_at_target()


@has_log
class HoldingState(State):
    def on_entry(self, dt: float) -> None:
        self.log: logging.Logger
        self.log.info("*********** ENTERED HOLD STATE")

    def in_state(self, dt: float) -> None:
        device = typing.cast("SimulatedCRYOSMS", self._context)
        device.check_is_at_target()


class TrippedState(State):
    def in_state(self, dt: float) -> None:
        pass


class RampingState(State):
    def in_state(self, dt: float) -> None:
        device = typing.cast("SimulatedCRYOSMS", self._context)
        # to avoid tests taking forever, ignoring actual rate in
        # favour of value that ramps between boundaries in roughly 8 seconds
        rate = 0.05
        target = device.ramp_target_value()
        constant = device.constant
        if device.is_output_mode_tesla:
            rate = rate * constant
        device.output = approaches.linear(device.output, target, rate, dt)
        device.check_is_at_target()
