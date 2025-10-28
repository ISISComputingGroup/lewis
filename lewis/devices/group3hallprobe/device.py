from collections import OrderedDict
from enum import Enum
from typing import Callable, assert_never

from lewis.devices import StateMachineDevice

from .states import DefaultState, State

GAUSS_PER_TESLA = 10_000.0


class Ranges(Enum):
    """
    Expresses a measurement range that a Probe can be in.

    Values and indices from device manual.
    """

    R0 = 0  # 0.3 Tesla range
    R1 = 1  # 0.6 Tesla range
    R2 = 2  # 1.2 Tesla range
    R3 = 3  # 3.0 Tesla range


def range_to_max_gauss(r: Ranges) -> float:
    match r:
        case Ranges.R0:
            return 0.3 * GAUSS_PER_TESLA
        case Ranges.R1:
            return 0.6 * GAUSS_PER_TESLA
        case Ranges.R2:
            return 1.2 * GAUSS_PER_TESLA
        case Ranges.R3:
            return 3.0 * GAUSS_PER_TESLA

    assert_never(r)


class Probe:
    """
    A single probe.
    """

    def __init__(self) -> None:
        self.field = 0.0
        self.temperature = 0.0
        self.sensor_range = Ranges.R3
        self.initialized = True

    def is_over_range(self) -> bool:
        return abs(self.field) > range_to_max_gauss(self.sensor_range)

    def initialize(self) -> None:
        self.sensor_range = Ranges.R3
        self.initialized = True


class SimulatedGroup3HallProbe(StateMachineDevice):
    def _initialize_data(self) -> None:
        """
        Initialize all of the device's attributes.
        """
        self.connected = True
        self.probes = {
            0: Probe(),
            1: Probe(),
            2: Probe(),
        }

    def reset(self) -> None:
        self._initialize_data()

    def backdoor_set_field(self, probe_id: int, field: float) -> None:
        self.probes[probe_id].field = field

    def backdoor_set_temperature(self, probe_id: int, temperature: float) -> None:
        self.probes[probe_id].temperature = temperature

    def backdoor_set_initialized(self, probe_id: int, initialized: bool) -> None:
        self.probes[probe_id].initialized = initialized

    def _get_state_handlers(self) -> dict[str, State]:
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self) -> str:
        return "default"

    def _get_transition_handlers(self) -> dict[tuple[str, str], Callable[[], bool]]:
        return OrderedDict([])
