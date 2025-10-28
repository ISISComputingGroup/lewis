from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


OUTMODE_INPUT = 1
OUTMODE_POWERUPENABLE = 2
OUTMODE_POLARITY = 3
OUTMODE_FILTER = 4
OUTMODE_DELAY = 5


@has_log
class Lakeshore372StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_tset").escape("SETP? 0").eos().build(),
        CmdBuilder("set_tset").escape("SETP 0 ").float().eos().build(),
        CmdBuilder("get_temperature").escape("RDGK? A").eos().build(),
        CmdBuilder("get_resistance").escape("RDGR? A").eos().build(),
        CmdBuilder("get_heater_range").escape("RANGE? 0").eos().build(),
        CmdBuilder("set_heater_range").escape("RANGE 0,").int().eos().build(),
        CmdBuilder("get_heater_power").escape("HTR?").eos().build(),
        CmdBuilder("get_pid").escape("PID? ").optional("0").eos().build(),
        CmdBuilder("set_pid")
        .escape("PID ")
        .float()
        .escape(",")
        .float()
        .escape(",")
        .float()
        .eos()
        .build(),
        CmdBuilder("get_outmode").escape("OUTMODE? 0").eos().build(),
        CmdBuilder("set_outmode")
        .escape("OUTMODE 0,")
        .int()
        .escape(",")
        .int()
        .escape(",")
        .int()
        .escape(",")
        .int()
        .escape(",")
        .int()
        .escape(",")
        .int()
        .eos()
        .build(),
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

    def set_tset(self, temperature):
        self._device.temperature = temperature

    @if_connected
    def get_tset(self):
        return "{:.3f}".format(self._device.temperature)

    @if_connected
    def get_temperature(self):
        return "{:.3f}".format(self._device.temperature)

    @if_connected
    def get_resistance(self):
        return "{:.6f}".format(self._device.sensor_resistance)

    def set_heater_range(self, heater_range):
        self._device.heater_range = heater_range

    @if_connected
    def get_heater_range(self):
        return "{:d}".format(self._device.heater_range)

    @if_connected
    def get_heater_power(self):
        return "{:.3f}".format(self._device.heater_power)

    @if_connected
    def get_pid(self):
        return "{:.6f},{:d},{:d}".format(self._device.p, self._device.i, self._device.d)

    def set_pid(self, p, i, d):
        self._device.p = p
        self._device.i = int(round(i))
        self._device.d = int(round(d))

    @if_connected
    def get_outmode(self):
        return "{:d},{:d},{:d},{:d},{:d},{:d}".format(
            self._device.control_mode,
            OUTMODE_INPUT,
            OUTMODE_POWERUPENABLE,
            OUTMODE_POLARITY,
            OUTMODE_FILTER,
            OUTMODE_DELAY,
        )

    def set_outmode(self, control_mode, inp, powerup_enable, polarity, filt, delay):
        if (
            inp != OUTMODE_INPUT
            or powerup_enable != OUTMODE_POWERUPENABLE
            or polarity != OUTMODE_POLARITY
            or filt != OUTMODE_FILTER
            or delay != OUTMODE_DELAY
        ):
            raise ValueError("Invalid parameters sent to set_outmode")
        self._device.control_mode = control_mode
