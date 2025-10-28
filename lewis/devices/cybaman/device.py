from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import InitializedState, MovingState, UninitializedState


class SimulatedCybaman(StateMachineDevice):
    """Simulated cyber man."""

    def _initialize_data(self):
        """Sets the initial state of the device."""
        self.connected = True

        self.a_setpoint = 0
        self.b_setpoint = 0
        self.c_setpoint = 0

        self.a = self.a_setpoint
        self.b = self.b_setpoint
        self.c = self.c_setpoint

        self.home_position_axis_a = 66
        self.home_position_axis_b = 77
        self.home_position_axis_c = 88

        self.initialized = False

    def _get_state_handlers(self):
        """Returns: states and their names"""
        return {
            InitializedState.NAME: InitializedState(),
            UninitializedState.NAME: UninitializedState(),
            MovingState.NAME: MovingState(),
        }

    def _get_initial_state(self):
        """Returns: the name of the initial state"""
        return UninitializedState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions"""
        return OrderedDict(
            [
                ((UninitializedState.NAME, InitializedState.NAME), lambda: self.initialized),
                ((InitializedState.NAME, UninitializedState.NAME), lambda: not self.initialized),
                ((MovingState.NAME, UninitializedState.NAME), lambda: not self.initialized),
                (
                    (InitializedState.NAME, MovingState.NAME),
                    lambda: self.a != self.a_setpoint
                    or self.b != self.b_setpoint
                    or self.c != self.c_setpoint,
                ),
                (
                    (MovingState.NAME, InitializedState.NAME),
                    lambda: self.a == self.a_setpoint
                    and self.b == self.b_setpoint
                    and self.c == self.c_setpoint,
                ),
            ]
        )

    def home_axis_a(self):
        self.a_setpoint = self.home_position_axis_a

    def home_axis_b(self):
        self.b_setpoint = self.home_position_axis_b

    def home_axis_c(self):
        self.c_setpoint = self.home_position_axis_c
