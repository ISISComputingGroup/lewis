from lewis.core.statemachine import State


class StaticRunningState(State):
    """This state does not emulate a randomly changing output value"""

    def in_state(self, dt):
        pass


class DefaultRunningState(State):
    """The current and voltage measurements while in this state randomly fluctuate"""

    def in_state(self, dt):
        self._context.update(dt)
