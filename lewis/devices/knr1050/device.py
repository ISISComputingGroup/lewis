import time
from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import (
    HoldState,
    IdleState,
    InitializingState,
    OffState,
    PurgeState,
    RunState,
    StandbyState,
)

states = OrderedDict(
    [
        ("INITIALIZING", InitializingState()),
        ("OFF", OffState()),
        ("IDLE", IdleState()),
        ("RUN", RunState()),
        ("HOLD", HoldState()),
        ("PURGE", PurgeState()),
        ("STANDBY", StandbyState()),
    ]
)


class SimulatedKnr1050(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.connected = True
        self.input_correct = True

        self.pump_on = False
        self.keep_last_values = False
        self.hold = False
        self.standby = False
        self.initializing = False
        self.remote = False

        self.pressure = 0
        self.pressure_limit_low = 0
        self.pressure_limit_high = 100
        self.flow_rate = 0.01
        self.current_flow_rate = 0.0

        self.concentrations = [100, 0, 0, 0]

        self.curr_program_run_time = False
        self.error_string = ""

    def reset(self):
        self._initialize_data()

    @property
    def time_stamp(self):
        """Returns:
        (int) current time in ms
        """
        return int(round(time.time() * 1000))

    @property
    def state_num(self):
        return list(states.keys()).index(self.state)

    @property
    def state(self):
        return self._csm.state

    def _get_state_handlers(self):
        return states

    def _get_initial_state(self):
        return "OFF"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("INITIALIZING", "IDLE"), lambda: self.initializing is False),
                (("IDLE", "OFF"), lambda: self.pump_on is False),
                (("OFF", "IDLE"), lambda: self.pump_on is True),
                (("RUN", "HOLD"), lambda: self.hold is True),
                (("RUN", "STANDBY"), lambda: self.standby is True),
            ]
        )
