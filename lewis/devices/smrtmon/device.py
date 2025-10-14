from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedSmrtmon(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.connected = True
        self.stat = [0.0] * 11
        self.oplm = [1.0] * 9
        self.lims = [2.0] * 9

    def reset_values(self):
        self._initialize_data()

    def set_stat(self, num_stat, stat_value):
        self.stat[num_stat] = stat_value

    def set_oplm(self, num_oplm, oplm_value):
        self.oplm[num_oplm] = oplm_value

    def set_lims(self, num_lims, lims_value):
        self.lims[num_lims] = lims_value

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
