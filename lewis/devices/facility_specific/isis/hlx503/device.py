from collections import OrderedDict

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import He3PotEmptyState, RegeneratingState, TemperatureControlState


@has_log
class SimulatedItc503(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.control_channel = 1
        self.p, self.i, self.d = 0, 0, 0
        self.control = 0
        self.autopid = False
        self.sweeping = False
        self.temperature_sp = 0
        self.autoheat = False
        self.heater_voltage = 0
        self.he3pot_low_plugged_in = True
        self.sorb_temp = 1.5
        self.he3pot_temp = 0
        self.onekpot_temp = 1.5

        self.helium_3_pot_empty = False
        self.drift_towards = 1.5  # Drift to 1.5K ~= temperature of 1K pot.
        self.drift_rate = 1

        # Set by tests, affects the response format of the device. Slightly different models of ITC will respond
        # differently
        self.report_sweep_state_with_leading_zero = False

    def _get_state_handlers(self):
        return {
            "temperature_control": TemperatureControlState(),
            "helium_3_empty": He3PotEmptyState(),
            "regenerating": RegeneratingState(),
        }

    def _get_initial_state(self):
        return "temperature_control"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (
                    ("temperature_control", "helium_3_empty"),
                    lambda: self.helium_3_pot_empty,
                ),
                (
                    ("helium_3_empty", "regenerating"),
                    lambda: self.control_channel == 1 and self.temperature_sp >= 30,
                ),
                (
                    ("temperature_control", "regenerating"),
                    lambda: self.control_channel == 1 and self.temperature_sp >= 30,
                ),
                (
                    ("regenerating", "temperature_control"),
                    lambda: self.sorb_temp >= 30 and not self.helium_3_pot_empty,
                ),
            ]
        )

    @property
    def temperature_1(self):
        return self.sorb_temp

    @property
    def temperature_2(self):
        if self.he3pot_low_plugged_in:
            return self.he3pot_temp
        else:
            return self.onekpot_temp

    @property
    def temperature_3(self):
        return self.he3pot_temp

    @property
    def temperature(self):
        if self.control_channel == 1:
            return self.temperature_1
        elif self.control_channel == 2:
            return self.temperature_2
        elif self.control_channel == 3:
            return self.temperature_3
        else:
            raise ValueError("Control channel incorrect")

    @property
    def mode(self):
        return int(self.autoheat)

    @mode.setter
    def mode(self, new_mode):
        self.autoheat = new_mode % 2 != 0

    @property
    def heater_percent(self):
        return self.heater_voltage

    def backdoor_plug_in_onekpot(self):
        self.he3pot_low_plugged_in = False

    def backdoor_plug_in_he3potlow(self):
        self.he3pot_low_plugged_in = True
