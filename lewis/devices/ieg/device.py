from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedIeg(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.unique_id = 123

        self.gas_valve_open = False
        self.buffer_valve_open = False
        self.pump_valve_open = False

        self.operatingmode = 0

        self.sample_pressure_high_limit = 100
        self.sample_pressure_low_limit = 10
        self.sample_pressure = 0

        self.error = 0

        self.buffer_pressure_high = True

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def is_sample_pressure_high(self):
        return self.sample_pressure > self.sample_pressure_high_limit

    def is_sample_pressure_low(self):
        return self.sample_pressure < self.sample_pressure_low_limit

    def get_id(self):
        return self.unique_id

    def get_pressure(self):
        return self.sample_pressure

    def get_error(self):
        return self.error

    def is_pump_valve_open(self):
        return self.pump_valve_open

    def is_buffer_valve_open(self):
        return self.buffer_valve_open

    def is_gas_valve_open(self):
        return self.gas_valve_open

    def get_operating_mode(self):
        return self.operatingmode

    def is_buffer_pressure_high(self):
        return self.buffer_pressure_high

    def set_operating_mode(self, mode):
        self.operatingmode = mode
