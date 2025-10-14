from collections import OrderedDict
from random import random

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedTti355(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.identity = "Thurlby Thandar,EL302P,0,v1.14"
        self.voltage = 0.00
        self.voltage_sp = 1.00
        self.current = 0.00
        self.current_limit_sp = 1.00
        self.output_status = "OUT OFF"
        self.output_mode = "M CV"
        self.error = "ERR 0"
        self._max_voltage = 35.0
        self._max_current = 5.0
        self.load_resistance = 10

    def reset(self):
        self._initialize_data()

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def calculate_potential_current(self, voltage):
        return voltage / self.load_resistance

    def calculate_actual_voltage(self):
        return self.get_current() * self.load_resistance

    def voltage_within_limits(self, voltage):
        return voltage <= self._max_voltage

    def get_voltage(self):
        if self.output_status == "OUT ON":
            if self.output_mode == "M CI":
                self.voltage = self.calculate_actual_voltage()
            else:
                self.voltage = self.voltage_sp + ((random() - 0.5) / 1000)
        else:
            self.voltage = (random() - 0.5) / 1000
        return self.voltage

    def set_voltage_sp(self, voltage):
        voltage = round(float(voltage), 2)
        if not self.voltage_within_limits(voltage):
            self.error = "ERR 2"
        else:
            self.voltage_sp = voltage
            if (
                self.calculate_potential_current(voltage) > self.current_limit_sp
                and self.output_status == "OUT ON"
            ):
                self.output_mode = "M CI"

    def current_within_limits(self, current):
        return current <= self._max_current

    def get_current(self):
        if self.output_status == "OUT ON" and self.output_mode == "M CI":
            self.current = self.current_limit_sp + ((random() - 0.5) / 1000)
        else:
            self.current = (random() - 0.5) / 1000
        return self.current

    def set_current_limit_sp(self, current):
        current = round(float(current), 2)
        if not self.current_within_limits(current):
            self.error = "ERR 2"
        else:
            self.current_limit_sp = current

    def set_output_status(self, status):
        if status == "ON":
            self.output_status = "OUT ON"
        elif status == "OFF":
            self.output_status = "OUT OFF"
            self.reset()

    def get_output_status(self):
        return self.output_status

    def get_output_mode(self):
        return self.output_mode

    def get_error_status(self):
        if self.error == "ERR 1":
            self.error = "ERR 0"
            return "ERR 1"
        elif self.error == "ERR 2":
            self.error = "ERR 0"
            return "ERR 2"
        else:
            return self.error
