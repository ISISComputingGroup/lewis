from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedLakeshore340(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.temp_a = 0
        self.temp_b = 0
        self.temp_c = 0
        self.temp_d = 0
        self.measurement_a = 0
        self.measurement_b = 0
        self.measurement_c = 0
        self.measurement_d = 0

        self.tset = 0

        self.p, self.i, self.d = 0, 0, 0

        self.pid_mode = 1
        self.loop_on = True

        self.max_temp = 0
        self.heater_output = 0
        self.heater_range = 0
        self.excitationa = 0

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
