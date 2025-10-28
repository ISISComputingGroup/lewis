from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder

_CONTROL_CHANNEL, _CONTROL_CHANNEL_INDEX = "B", 1
_SENSOR_UNITS = 1
_POWERUPENABLE = 1


@has_log
class Lakeshore340StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_temperature_a").escape("KRDG? 0").eos().build(),
        CmdBuilder("get_temperature_b").escape("KRDG? 1").eos().build(),
        CmdBuilder("get_temperature_c").escape("KRDG? 2").eos().build(),
        CmdBuilder("get_temperature_d").escape("KRDG? 3").eos().build(),
        CmdBuilder("get_measurement_a").escape("SRDG? 0").eos().build(),
        CmdBuilder("get_measurement_b").escape("SRDG? 1").eos().build(),
        CmdBuilder("get_measurement_c").escape("SRDG? 2").eos().build(),
        CmdBuilder("get_measurement_d").escape("SRDG? 3").eos().build(),
        CmdBuilder("set_tset")
        .escape("SETP {},".format(_CONTROL_CHANNEL_INDEX))
        .float()
        .eos()
        .build(),
        CmdBuilder("get_tset").escape("SETP? {}".format(_CONTROL_CHANNEL_INDEX)).eos().build(),
        CmdBuilder("set_pid")
        .escape("PID {},".format(_CONTROL_CHANNEL_INDEX))
        .float()
        .escape(",")
        .float()
        .escape(",")
        .int()
        .eos()
        .build(),
        CmdBuilder("get_pid").escape("PID? {}".format(_CONTROL_CHANNEL_INDEX)).eos().build(),
        CmdBuilder("set_pid_mode")
        .escape("CMODE {},".format(_CONTROL_CHANNEL_INDEX))
        .int()
        .eos()
        .build(),
        CmdBuilder("get_pid_mode").escape("CMODE? {}".format(_CONTROL_CHANNEL_INDEX)).eos().build(),
        CmdBuilder("set_control_mode")
        .escape("CSET {},{},{},".format(_CONTROL_CHANNEL_INDEX, _CONTROL_CHANNEL, _SENSOR_UNITS))
        .int()
        .escape(",{}".format(_POWERUPENABLE))
        .eos()
        .build(),
        CmdBuilder("get_control_mode")
        .escape("CSET? {}".format(_CONTROL_CHANNEL_INDEX))
        .eos()
        .build(),
        CmdBuilder("set_temp_limit")
        .escape("CLIMIT {},".format(_CONTROL_CHANNEL_INDEX))
        .float()
        .eos()
        .build(),
        CmdBuilder("get_temp_limit")
        .escape("CLIMIT? {}".format(_CONTROL_CHANNEL_INDEX))
        .eos()
        .build(),
        CmdBuilder("get_heater_output").escape("HTR?").eos().build(),
        CmdBuilder("set_heater_range").escape("RANGE ").int().eos().build(),
        CmdBuilder("get_heater_range").escape("RANGE?").eos().build(),
        CmdBuilder("get_excitation_a").escape("INTYPE? A").eos().build(),
        CmdBuilder("set_excitation_a").escape("INTYPE A, 1, , , , ").int().eos().build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    def get_temperature_a(self):
        return self._device.temp_a

    def get_temperature_b(self):
        return self._device.temp_b

    def get_temperature_c(self):
        return self._device.temp_c

    def get_temperature_d(self):
        return self._device.temp_d

    def get_measurement_a(self):
        return self._device.measurement_a

    def get_measurement_b(self):
        return self._device.measurement_b

    def get_measurement_c(self):
        return self._device.measurement_c

    def get_measurement_d(self):
        return self._device.measurement_d

    def set_tset(self, val):
        self._device.tset = float(val)

    def get_tset(self):
        return self._device.tset

    def set_pid(self, p, i, d):
        self._device.p, self._device.i, self._device.d = p, i, d

    def get_pid(self):
        return "{},{},{}".format(self._device.p, self._device.i, self._device.d)

    def get_pid_mode(self):
        return self._device.pid_mode

    def set_pid_mode(self, mode):
        if not 1 <= mode <= 6:
            raise ValueError("Mode must be 1-6")
        self._device.pid_mode = mode

    def get_control_mode(self):
        return "{},{},{},{}".format(
            _CONTROL_CHANNEL, _SENSOR_UNITS, 1 if self._device.loop_on else 0, _POWERUPENABLE
        )

    def set_control_mode(self, val):
        self._device.loop_on = bool(val)

    def set_temp_limit(self, val):
        self._device.max_temp = val

    def get_temp_limit(self):
        return "{},0,0,0,0".format(self._device.max_temp)

    def get_heater_output(self):
        return "{:.2f}".format(self._device.heater_output)

    def get_heater_range(self):
        return self._device.heater_range

    def set_heater_range(self, val):
        if not 0 <= val <= 5:
            raise ValueError("Heater range must be 0-5")
        self._device.heater_range = val

    def get_excitation_a(self):
        return self._device.excitationa

    def set_excitation_a(self, val):
        if not 0 <= val <= 12:
            raise ValueError("Excitations range must be 0-12")
        self._device.excitationa = val
