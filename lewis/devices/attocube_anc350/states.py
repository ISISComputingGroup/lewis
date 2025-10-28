from lewis.core import approaches
from lewis.core.statemachine import State


class MovingState(State):
    """Device is in moving state."""

    NAME = "Moving"

    def in_state(self, dt):
        device = self._context
        device.position = approaches.linear(
            device.position, device.position_setpoint, device.speed, dt
        )


class DefaultState(State):
    NAME = "Default"

    def on_entry(self, dt):
        self._context.start_move = False
