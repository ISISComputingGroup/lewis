from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState, MovingState


class SimulatedAttocubeANC350(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.connected = True
        self.position = 0
        self.position_setpoint = 0
        self.speed = 10
        self.start_move = False
        self.amplitude = 30000
        self.axis_on = True

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude

    def move(self):
        self.start_move = True

    def set_position_setpoint(self, position):
        self.position_setpoint = position

    def set_axis_on(self, on_state):
        self.axis_on = on_state == 1

    def _get_state_handlers(self):
        return {DefaultState.NAME: DefaultState(), MovingState.NAME: MovingState()}

    def _get_initial_state(self):
        return DefaultState.NAME

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                ((DefaultState.NAME, MovingState.NAME), lambda: self.start_move and self.axis_on),
                (
                    (MovingState.NAME, DefaultState.NAME),
                    lambda: self.position_setpoint == self.position,
                ),
            ]
        )
