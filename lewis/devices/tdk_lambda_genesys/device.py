from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedTDKLambdaGenesys(StateMachineDevice):
    def _initialize_data(self):
        self._voltage = 10.0
        self._current = 2.0
        self._setpoint_voltage = 10.0
        self._setpoint_current = 2.0
        self._powerstate = "OFF"
        self.comms_initialized = False

    def _get_state_handlers(self):
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        return DefaultState.NAME

    def _get_transition_handlers(self):
        return OrderedDict()

    @property
    def voltage(self):
        # Return current actual voltage
        return self._voltage

    @property
    def setpoint_voltage(self):
        # Return the set voltage
        return self._setpoint_voltage

    @property
    def current(self):
        return self._current

    @property
    def setpoint_current(self):
        return self._setpoint_current

    @property
    def powerstate(self):
        return self._powerstate

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage

    @setpoint_voltage.setter
    def setpoint_voltage(self, spv):
        self._setpoint_voltage = spv

    @current.setter
    def current(self, c):
        self._current = c

    @setpoint_current.setter
    def setpoint_current(self, c):
        self._setpoint_current = c

    @powerstate.setter
    def powerstate(self, p):
        self._powerstate = p
