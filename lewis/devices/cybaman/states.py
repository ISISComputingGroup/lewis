from lewis.core import approaches
from lewis.core.statemachine import State


class UninitializedState(State):
    NAME = "UninitializedState"

    def on_entry(self, dt):
        print("Entering uninitialized state")


class InitializedState(State):
    NAME = "InitializedState"

    def on_entry(self, dt):
        print("Entering initialized state")


class MovingState(State):
    NAME = "MovingState"

    def in_state(self, dt):
        device = self._context

        device.a = approaches.linear(device.a, device.a_setpoint, 10, dt)
        device.b = approaches.linear(device.b, device.b_setpoint, 10, dt)
        device.c = approaches.linear(device.c, device.c_setpoint, 10, dt)

    def on_entry(self, dt):
        print("Entering moving state")
