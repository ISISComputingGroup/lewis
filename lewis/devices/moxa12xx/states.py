from lewis.core.statemachine import State


class DefaultState(State):
    """Device is in default state.
    """

    NAME = "Default"

    def in_state(self, dt):
        pass
