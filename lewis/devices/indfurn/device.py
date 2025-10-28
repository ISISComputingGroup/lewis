from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SampleHolderMaterials(object):
    ALUMINIUM = 0
    GLASSY_CARBON = 1
    GRAPHITE = 2
    QUARTZ = 3
    SINGLE_CRYSTAL_SAPPHIRE = 4
    STEEL = 5
    VANADIUM = 6


class SimulatedIndfurn(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.setpoint = 20
        self.pipe_temperature = 25.1
        self.capacitor_bank_temperature = 30.3
        self.fet_temperature = 35.8

        self.p, self.i, self.d = 0, 0, 0
        self.sample_time = 100

        self.direction_heating = True

        self.pid_lower_limit, self.pid_upper_limit = 0, 0

        self.pid_mode_automatic = True
        self.running = True

        self.psu_voltage, self.psu_current, self.output = 0, 0, 0

        self.remote_mode = True
        self.power_supply_on = True
        self.sample_area_led_on = True
        self.hf_on = False

        self.psu_overtemp, self.psu_overvolt = False, False
        self.cooling_water_flow = 100

        self.sample_holder_material = SampleHolderMaterials.ALUMINIUM

        self.thermocouple_1_fault, self.thermocouple_2_fault = 0, 0

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def is_cooling_water_flow_ok(self):
        return self.cooling_water_flow >= 100
