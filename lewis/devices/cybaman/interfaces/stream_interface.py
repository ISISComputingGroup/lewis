from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


class CybamanStreamInterface(StreamInterface):
    """Stream interface for the serial port"""

    FLOAT = "([-+]?[0-9]*\.?[0-9]*)"

    commands = {
        Cmd("initialize", "^A$"),
        Cmd("get_a", "^M101$"),
        Cmd("get_b", "^M201$"),
        Cmd("get_c", "^M301$"),
        Cmd(
            "set_all",
            "^OPEN PROG 10 CLEAR\nG1 A "
            + FLOAT
            + " B "
            + FLOAT
            + " C "
            + FLOAT
            + " TM([0-9]*)$",
        ),
        Cmd("ignore", "^CLOSE$"),
        Cmd("ignore", "^B10R$"),
        Cmd("reset", "^\$\$\$$"),
        Cmd("home_a", "^B9001R$"),
        Cmd("home_b", "^B9002R$"),
        Cmd("home_c", "^B9003R$"),
        Cmd("stop", "^{}$".format(chr(0x01))),
    }

    in_terminator = "\r"

    # ACK character
    out_terminator = chr(0x06)

    @has_log
    def handle_error(self, request, error):
        """If command is not recognised print and error.

        :param request: requested string
        :param error: problem
        :return:
        """
        error = "An error occurred at request " + repr(request) + ": " + repr(error)
        print(error)
        self.log.debug(error)
        return error

    @if_connected
    def ignore(self):
        return ""

    @if_connected
    def initialize(self):
        self._device.initialized = True
        return ""

    @if_connected
    def stop(self):
        self._device.initialized = False

    @if_connected
    def reset(self):
        self._device._initialize_data()
        return ""

    @if_connected
    def get_a(self):
        return "{}\r".format(self._device.a * 3577)

    @if_connected
    def get_b(self):
        return "{}\r".format(self._device.b * 3663)

    @if_connected
    def get_c(self):
        return "{}\r".format(self._device.c * 3663)

    @if_connected
    def set_all(self, a, b, c, tm):
        self._verify_tm(a, b, c, tm)

        self._device.a_setpoint = float(a)
        self._device.b_setpoint = float(b)
        self._device.c_setpoint = float(c)
        return ""

    def _verify_tm(self, a, b, c, tm):
        tm = int(tm)
        old_position = (self._device.a, self._device.b, self._device.c)
        new_position = (float(a), float(b), float(c))

        max_difference = max([abs(a - b) for a, b in zip(old_position, new_position)])
        expected_tm = max([int(round(max_difference / 5.0)) * 1000, 4000])

        # Allow a difference of 1000 for rounding errors / differences between labview and epics
        # (error would get multiplied by 1000)
        if abs(tm - expected_tm) > 1000:
            assert False, "Wrong TM value! Expected {} but got {}".format(
                expected_tm, tm
            )

    def home_a(self):
        self._device.home_axis_a()
        return ""

    def home_b(self):
        self._device.home_axis_b()
        return ""

    def home_c(self):
        self._device.home_axis_c()
        return ""
