from datetime import datetime

from lewis.devices.triton.device import HEATER_NAME

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder


@has_log
class TritonStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        # ID
        CmdBuilder("get_idn").escape("*IDN?").eos().build(),
        # UIDs
        CmdBuilder("get_uid")
        .escape("READ:SYS:DR:CHAN:")
        .arg("[A-Z0-9]+")
        .eos()
        .build(),
        # PID setpoints
        CmdBuilder("set_p")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:P:")
        .float()
        .eos()
        .build(),
        CmdBuilder("set_i")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:I:")
        .float()
        .eos()
        .build(),
        CmdBuilder("set_d")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:D:")
        .float()
        .eos()
        .build(),
        # PID readbacks
        CmdBuilder("get_p")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:P")
        .eos()
        .build(),
        CmdBuilder("get_i")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:I")
        .eos()
        .build(),
        CmdBuilder("get_d")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:D")
        .eos()
        .build(),
        # Setpoint temperature
        CmdBuilder("set_temperature_setpoint")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:TSET:")
        .float()
        .eos()
        .build(),
        CmdBuilder("get_temperature_setpoint")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:TSET")
        .eos()
        .build(),
        # Temperature
        CmdBuilder("get_temp")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:SIG:TEMP")
        .eos()
        .build(),
        # Heater range
        CmdBuilder("set_heater_range")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:RANGE:")
        .float()
        .eos()
        .build(),
        CmdBuilder("get_heater_range")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:RANGE")
        .eos()
        .build(),
        # Heater type
        CmdBuilder("get_heater_type")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:HTR")
        .eos()
        .build(),
        # Get heater power
        CmdBuilder("get_heater_power")
        .escape("READ:DEV:{}:HTR:SIG:POWR".format(HEATER_NAME))
        .eos()
        .build(),
        # Get heater resistance
        CmdBuilder("get_heater_resistance")
        .escape("READ:DEV:{}:HTR:RES".format(HEATER_NAME))
        .eos()
        .build(),
        # Heater control sensor
        CmdBuilder("get_heater_control_sensor")
        .escape("READ:DEV:{}:HTR:LOOP".format(HEATER_NAME))
        .eos()
        .build(),
        # Loop mode
        CmdBuilder("get_closed_loop_mode")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:MODE")
        .eos()
        .build(),
        CmdBuilder("set_closed_loop_mode")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:LOOP:MODE:")
        .any()
        .eos()
        .build(),
        # Channel enablement
        CmdBuilder("get_channel_enabled")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:MEAS:ENAB")
        .eos()
        .build(),
        CmdBuilder("set_channel_enabled")
        .escape("SET:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:MEAS:ENAB:")
        .any()
        .eos()
        .build(),
        # Status
        CmdBuilder("get_status").escape("READ:SYS:DR:STATUS").eos().build(),
        CmdBuilder("get_automation").escape("READ:SYS:DR:ACTN").eos().build(),
        # Pressures
        CmdBuilder("get_pressure")
        .escape("READ:DEV:")
        .arg("P[0-9]+")
        .escape(":PRES:SIG:PRES")
        .eos()
        .build(),
        # System
        CmdBuilder("get_time").escape("READ:SYS:TIME").eos().build(),
        # Sensor info
        CmdBuilder("get_sig")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:SIG")
        .eos()
        .build(),
        CmdBuilder("get_excitation")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:EXCT")
        .eos()
        .build(),
        CmdBuilder("get_meas")
        .escape("READ:DEV:")
        .arg("T[0-9]+")
        .escape(":TEMP:MEAS")
        .eos()
        .build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    def raise_if_channel_is_not_sample_channel(self, chan):
        if str(chan) != self.device.sample_channel:
            raise ValueError("Channel should have been sample channel")

    def get_idn(self):
        return "This is the IDN of this device"

    def get_uid(self, chan):
        return "STAT:SYS:DR:CHAN:{}:{}".format(
            chan, self.device.find_temperature_channel(chan)
        )

    def set_p(self, stage, value):
        self.raise_if_channel_is_not_sample_channel(stage)
        self.device.set_p(float(value))
        return "ok"

    def set_i(self, stage, value):
        self.raise_if_channel_is_not_sample_channel(stage)
        self.device.set_i(float(value))
        return "ok"

    def set_d(self, stage, value):
        self.raise_if_channel_is_not_sample_channel(stage)
        self.device.set_d(float(value))
        return "ok"

    def get_p(self, stage):
        self.raise_if_channel_is_not_sample_channel(stage)
        return "STAT:DEV:{}:TEMP:LOOP:P:{}".format(stage, self.device.get_p())

    def get_i(self, stage):
        self.raise_if_channel_is_not_sample_channel(stage)
        return "STAT:DEV:{}:TEMP:LOOP:I:{}".format(stage, self.device.get_i())

    def get_d(self, stage):
        self.raise_if_channel_is_not_sample_channel(stage)
        return "STAT:DEV:{}:TEMP:LOOP:D:{}".format(stage, self.device.get_d())

    def set_temperature_setpoint(self, chan, value):
        self.raise_if_channel_is_not_sample_channel(chan)
        self.device.set_temperature_setpoint(float(value))
        return "ok"

    def get_temperature_setpoint(self, chan):
        self.raise_if_channel_is_not_sample_channel(chan)
        return "STAT:DEV:{}:TEMP:LOOP:TSET:{}K".format(
            chan, self.device.get_temperature_setpoint()
        )

    def set_heater_range(self, chan, value):
        self.raise_if_channel_is_not_sample_channel(chan)
        self.device.set_heater_range(float(value))
        return "ok"

    def get_heater_range(self, chan):
        self.raise_if_channel_is_not_sample_channel(chan)
        return "STAT:DEV:{}:TEMP:LOOP:RANGE:{}mA".format(
            chan, self.device.get_heater_range()
        )

    def get_heater_type(self, chan):
        self.raise_if_channel_is_not_sample_channel(chan)
        return "STAT:DEV:{}:TEMP:LOOP:HTR:{}".format(chan, HEATER_NAME)

    def get_heater_power(self):
        return "STAT:DEV:{}:HTR:SIG:POWR:{}uW".format(
            HEATER_NAME, self.device.heater_power
        )

    def get_heater_resistance(self):
        return "STAT:DEV:{}:HTR:RES:{}Ohm".format(
            HEATER_NAME, self.device.heater_resistance
        )

    def get_heater_current(self):
        return "STAT:DEV:{}:HTR:SIG:CURR:{}mA".format(
            HEATER_NAME, self.device.heater_current
        )

    def get_closed_loop_mode(self, chan):
        self.raise_if_channel_is_not_sample_channel(chan)
        return "STAT:DEV:{}:TEMP:LOOP:MODE:{}".format(
            chan, "ON" if self.device.get_closed_loop_mode() else "OFF"
        )

    def set_closed_loop_mode(self, chan, mode):
        self.raise_if_channel_is_not_sample_channel(chan)

        if mode not in ["ON", "OFF"]:
            raise ValueError("Invalid mode")

        self.device.set_closed_loop_mode(mode == "ON")
        return "STAT:SET:DEV:{}:TEMP:LOOP:MODE:{}:VALID".format(chan, mode)

    def get_channel_enabled(self, channel):
        return "STAT:DEV:{}:TEMP:MEAS:ENAB:{}".format(
            channel, "ON" if self.device.is_channel_enabled(channel) else "OFF"
        )

    def set_channel_enabled(self, channel, newstate):
        newstate = str(newstate)

        if newstate not in ["ON", "OFF"]:
            raise ValueError("New state '{}' not valid.".format(newstate))

        self.device.set_channel_enabled(channel, newstate == "ON")
        return "ok"

    def get_status(self):
        return "STAT:SYS:DR:STATUS:{}".format(self.device.get_status())

    def get_automation(self):
        return "STAT:SYS:DR:ACTN:{}".format(self.device.get_automation())

    def get_temp(self, stage):
        return "STAT:DEV:{}:TEMP:SIG:TEMP:{}K".format(
            stage, self.device.get_temp(str(stage))
        )

    def get_pressure(self, sensor):
        return "STAT:DEV:{}:PRES:SIG:PRES:{}mB".format(
            sensor, self.device.get_pressure(sensor)
        )

    def get_time(self):
        return datetime.now().strftime("STAT:SYS:TIME:%H:%M:%S")

    def get_heater_control_sensor(self):
        # Always assume heater controls sample. This is true so far at ISIS
        return "STAT:DEV:{}:HTR:LOOP:SENS:{}".format(
            HEATER_NAME, self.device.sample_channel
        )

    def get_sig(self, chan):
        return "STAT:DEV:{}:TEMP:SIG:TEMP:{}K:RES:{}Ohm".format(
            chan,
            self.device.temperature_stages[chan].temperature,
            self.device.temperature_stages[chan].resistance,
        )

    def get_excitation(self, chan):
        return "STAT:DEV:{}:TEMP:EXCT:TYPE:{}:MAG:{}V".format(
            chan,
            self.device.temperature_stages[chan].excitation_type,
            self.device.temperature_stages[chan].excitation,
        )

    def get_meas(self, chan):
        return "STAT:DEV:{}:TEMP:MEAS:PAUS:{}s:DWEL:{}s:ENAB:ON".format(
            chan,
            self.device.temperature_stages[chan].pause,
            self.device.temperature_stages[chan].dwell,
        )
