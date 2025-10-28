from lewis.core import approaches
from lewis.core.statemachine import State


class DefaultState(State):
    def in_state(self, dt):
        device = self._context

        rate = 10

        device.temperature = approaches.linear(
            device.temperature, device.temperature_sp, rate, dt
        )
