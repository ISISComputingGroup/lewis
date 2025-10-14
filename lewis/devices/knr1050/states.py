from lewis.core.statemachine import State


class InitializingState(State):
    pass


class OffState(State):
    pass


class IdleState(State):
    pass


class RunState(State):
    pass


class HoldState(State):
    pass


class PurgeState(State):
    pass


class StandbyState(State):
    pass
