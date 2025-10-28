from lewis.core.logging import has_log
from lewis.core.statemachine import State


@has_log
class DefaultState(State):
    """Device is in default state."""

    NAME = "Default"

    def in_state(self, dt):
        pass
