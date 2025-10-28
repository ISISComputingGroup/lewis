from lewis.core import approaches
from lewis.core.statemachine import State


class DefaultNotCirculatingState(State):
    pass


class DefaultCirculatingState(State):
    def in_state(self, dt):
        # Approach target temperature at a set rate
        self._context.temperature = approaches.linear(
            self._context.temperature,
            self._context.set_point_temperature,
            self._context.heating_power / 60.0,
            dt,
        )
