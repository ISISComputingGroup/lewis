from lewis.core.statemachine import State


class DefaultInitState(State):
    pass


class DefaultRunningState(State):
    def in_state(self, dt):
        self._context.update_pressures(dt)
