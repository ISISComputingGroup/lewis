from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import PumpOff, PumpOn, PumpProgram, PumpProgramReset

states = OrderedDict(
    [
        ("pump_off", PumpOff()),
        ("pump_on", PumpOn()),
        ("pump_program", PumpProgram()),
        ("pump_program_reset", PumpProgramReset()),
    ]
)


class SimulatedJsco4180(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.connected = True
        self.input_correct = True
        self.single_channel_mode = False
        self.status = "pump_off"

        self.flowrate_sp = 0.1
        self.flowrate_rbv = 0.1
        self.flowrate = 0.0

        self.pressure = 0
        self.pressure_max = 400
        self.pressure_min = 1

        # Composition components A, B, C, D
        self.component_A = 100.0
        self.component_B = 0.0
        self.component_C = 0.0
        self.component_D = 0.0

        self.program_runtime = 0
        self.file_number = 0
        self.file_open = False
        self.error = 0

    @property
    def state(self):
        return self._csm.state

    def crash_pump(self):
        self.connected = False

    def simulate_pumping(self):
        self.flowrate = self.flowrate_rbv
        self.pressure = (self.pressure_max - self.pressure_min) // 2

    def _get_state_handlers(self):
        return states

    def _get_initial_state(self):
        return "pump_off"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("pump_off", "pump_on"), lambda: self.status == "on"),
                (("pump_off", "pump_program"), lambda: self.status == "pump_program"),
                (("pump_off", "pump_program_reset"), lambda: self.status == "pump_program_reset"),
                (("pump_on", "pump_off"), lambda: self.status == "pump_off"),
                (("pump_on", "pump_program"), lambda: self.status == "pump_program"),
                (("pump_on", "pump_program_reset"), lambda: self.status == "pump_program_reset"),
                (("pump_program", "pump_off"), lambda: self.status == "pump_off"),
                (("pump_program", "pump_on"), lambda: self.status == "pump_on"),
                (
                    ("pump_program", "pump_program_reset"),
                    lambda: self.status == "pump_program_reset",
                ),
                (("pump_program_reset", "pump_off"), lambda: self.status == "pump_off"),
                (("pump_program_reset", "pump_on"), lambda: self.status == "pump_on"),
                (("pump_program_reset", "pump_program"), lambda: self.status == "pump_program"),
            ]
        )

    def reset(self):
        self._initialize_data()
