from lewis.core import approaches
from lewis.core.statemachine import State


class DefaultState(State):
    pass


class StoppingState(State):
    def in_state(self, dt):
        device = self._context
        device.frequency = approaches.linear(device.frequency, 0, 50, dt)


class GoingState(State):
    def in_state(self, dt):
        device = self._context
        device.frequency = approaches.linear(
            device.frequency, device.frequency_setpoint, 50, dt
        )
