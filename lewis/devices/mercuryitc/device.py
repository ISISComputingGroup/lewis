from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import DefaultState


class ChannelTypes(object):
    TEMP = "TEMP"
    HTR = "HTR"
    AUX = "AUX"
    PRES = "PRES"
    LVL = "LVL"


class Channel(object):
    def __init__(self, channel_type, nickname):
        super(Channel, self).__init__()
        self.channel_type = channel_type
        self.nickname = nickname


class TempPressureCommonChannel(Channel):
    """Holds attributes common to temperature and pressure channels
    """

    def __init__(self, channel_type, nickname):
        super(TempPressureCommonChannel, self).__init__(channel_type, nickname)

        # PID control loop settings
        self.autopid = False
        self.autopid_file = "sim_autopid_file"
        self.p = 0
        self.i = 0
        self.d = 0

        # Needle valve & heater settings
        self.gas_flow_auto = True
        self.heater_auto = True
        self.heater_percent = 0

        # Associated channels
        self.associated_heater_channel = None
        self.associated_aux_channel = None

        # Calibration
        self.calibration_file = "sim_calib_file"


class TemperatureChannel(TempPressureCommonChannel):
    def __init__(self, nickname):
        super(TemperatureChannel, self).__init__(ChannelTypes.TEMP, nickname)

        self.temperature = 0
        self.temperature_sp = 0
        self.resistance = 0


class PressureChannel(TempPressureCommonChannel):
    def __init__(self, nickname):
        super(PressureChannel, self).__init__(ChannelTypes.PRES, nickname)

        self.pressure = 0
        self.pressure_sp = 0
        self.voltage = 0


class HeaterChannel(Channel):
    def __init__(self, nickname):
        super(HeaterChannel, self).__init__(ChannelTypes.HTR, nickname)

        self.power = 0
        self.voltage = 0
        self.current = 0
        self.voltage_limit = 0


class AuxChannel(Channel):
    def __init__(self, nickname):
        super(AuxChannel, self).__init__(ChannelTypes.AUX, nickname)

        self.gas_flow = 0


class LevelChannel(Channel):
    def __init__(self, nickname):
        super(LevelChannel, self).__init__(ChannelTypes.LVL, nickname)

        self.nitrogen_level = 0
        self.helium_level = 0
        self.slow_helium_read_rate = False


@has_log
class SimulatedMercuryitc(StateMachineDevice):
    def _initialize_data(self):
        self.connected = True

        self.resistance_suffix = "O"

        self.channels = {
            # Temperature channel 1
            "MB0.T0": TemperatureChannel("MB0.T0"),
            "MB1.H0": HeaterChannel("DB0.H0"),
            "DB1.A0": AuxChannel("DB1.A0"),
            # Temperature channel 2
            "DB2.T1": TemperatureChannel("DB2.T1"),
            "DB3.H1": HeaterChannel("DB3.H1"),
            "DB4.A1": AuxChannel("DB4.A1"),
            # Pressure channel 1
            "DB5.P0": PressureChannel("DB5.P0"),
            "DB6.H2": HeaterChannel("DB6.H2"),
            "DB7.A2": AuxChannel("DB7.A2"),
            # Pressure channel 2
            "DB5.P1": PressureChannel("DB5.P1"),
            "DB6.H3": HeaterChannel("DB6.H3"),
            "DB7.A3": AuxChannel("DB7.A3"),
            # Level channel 1
            "DB8.L0": LevelChannel("DB8.L0"),
        }

        # Associate each temperature/pressure channel with a heater and an auxilary channel:
        self.channels["MB0.T0"].associated_heater_channel = "MB1.H0"
        self.channels["MB0.T0"].associated_aux_channel = "DB1.A0"

        self.channels["DB2.T1"].associated_heater_channel = "DB3.H1"
        self.channels["DB2.T1"].associated_aux_channel = "DB4.A1"

        self.channels["DB5.P0"].associated_heater_channel = "DB6.H2"
        self.channels["DB5.P0"].associated_aux_channel = "DB7.A2"

        self.channels["DB5.P1"].associated_heater_channel = "DB6.H3"
        self.channels["DB5.P1"].associated_aux_channel = "DB7.A3"

    def reset(self):
        self._initialize_data()

    def _get_state_handlers(self):
        return {"default": DefaultState()}

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def backdoor_set_channel_property(self, chan_id, property_name, value):
        assert hasattr(self.channels[chan_id], property_name)
        setattr(self.channels[chan_id], property_name, value)
