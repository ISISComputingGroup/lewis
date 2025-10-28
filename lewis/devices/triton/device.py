from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState

HEATER_NAME = "H1"


class TemperatureStage(object):
    """Class representing a temperature stage."""

    def __init__(self, name):
        self.name = name
        self.temperature = 1
        self.enabled = True

        self.resistance = 0

        self.excitation_type = "VOLT"
        self.excitation = 10

        self.pause = 10
        self.dwell = 3


class PressureSensor(object):
    """Class to represent a pressure sensor.

    Having this as a class makes it more extensible in future, as the triton driver is still in flux.
    """

    def __init__(self):
        self.pressure = 0


class SimulatedTriton(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.heater_range = 0
        self.heater_power = 1
        self.heater_resistance = 0

        self.temperature_setpoint = 0
        self.p = 0
        self.i = 0
        self.d = 0
        self.closed_loop = False

        self.status = "This is a device status message."
        self.automation = "This is the automation status"

        self.pressure_sensors = {"P{}".format(i): PressureSensor() for i in range(1, 6)}

        self.temperature_stages = {
            "T1": TemperatureStage("STIL"),
            "T2": TemperatureStage("PT1"),
            "T3": TemperatureStage("PT2"),
            "T4": TemperatureStage("SORB"),
            "T5": TemperatureStage("MC"),
            "T6": TemperatureStage("unknown"),
        }

        self.sample_channel = "T5"
        assert self.sample_channel in self.temperature_stages

    def find_temperature_channel(self, name):
        for k, v in self.temperature_stages.items():
            if v.name == name:
                return k
        else:
            raise KeyError("{} not found".format(name))

    def set_temperature_backdoor(self, stage_name, new_temp):
        self.temperature_stages[self.find_temperature_channel(stage_name)].temperature = new_temp

    def set_pressure_backdoor(self, sensor, newpressure):
        self.pressure_sensors["P{}".format(sensor)].pressure = float(newpressure)

    def set_sensor_property_backdoor(self, sensor, property, value):
        # In older versions of the software, there was an off-by-one error here in the OI software.
        # This has now been fixed by O.I. so no longer need to adjust by one here.
        setattr(self.temperature_stages["T{}".format(sensor)], property, value)

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def get_closed_loop_mode(self):
        return self.closed_loop

    def set_closed_loop_mode(self, mode):
        self.closed_loop = mode

    def set_p(self, value):
        self.p = value

    def set_i(self, value):
        self.i = value

    def set_d(self, value):
        self.d = value

    def get_p(self):
        return self.p

    def get_i(self):
        return self.i

    def get_d(self):
        return self.d

    def get_temperature_setpoint(self):
        return self.temperature_setpoint

    def set_temperature_setpoint(self, value):
        self.temperature_setpoint = value

    def get_heater_range(self):
        return self.heater_range

    def set_heater_range(self, value):
        self.heater_range = value

    def is_channel_enabled(self, chan):
        try:
            return self.temperature_stages[chan].enabled
        except KeyError:
            return False

    def set_channel_enabled(self, chan, newstate):
        self.temperature_stages[chan].enabled = newstate

    def get_status(self):
        return self.status

    def get_automation(self):
        return self.automation

    def get_pressure(self, sensor):
        return self.pressure_sensors[sensor].pressure

    def get_temp(self, stage):
        return self.temperature_stages[stage].temperature
