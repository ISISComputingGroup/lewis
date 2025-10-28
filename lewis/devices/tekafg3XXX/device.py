from collections import OrderedDict
from typing import Any

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SourceChannel:
    def __init__(self) -> None:
        self.status = 0
        self.function = "SIN"
        self.polarity = "NORM"
        self.impedance = 0.0
        self.voltage = 0.0
        self.voltage_units = "VPP"
        self.voltage_low_limit = 0.0
        self.voltage_low_level = 0.0
        self.voltage_high_limit = 0.0
        self.voltage_high_level = 0.0
        self.voltage_offset = 0.0
        self.frequency = 0.0
        self.frequency_mode = "FIX"
        self.phase = 0.0
        self.burst_status = "OFF"
        self.burst_mode = "TRIG"
        self.burst_num_cycles = 0
        self.burst_time_delay = 0.0
        self.sweep_span = 0.0
        self.sweep_start = 0.0
        self.sweep_stop = 0.0
        self.sweep_hold_time = 0.0
        self.sweep_mode = "AUTO"
        self.sweep_return_time = 0.0
        self.sweep_spacing = "LIN"
        self.sweep_time = 0.0
        self.ramp_symmetry = 0.0


class SimulatedTekafg3XXX(StateMachineDevice):
    def _initialize_data(self) -> None:
        """Initialize all of the device's attributes."""
        self.connected = True
        self.channels = {1: SourceChannel(), 2: SourceChannel()}
        self.triggered = False

    def _get_state_handlers(self) -> dict[str, Any]:
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self) -> str:
        return "default"

    def _get_transition_handlers(self) -> OrderedDict[Any, Any]:
        return OrderedDict([])
