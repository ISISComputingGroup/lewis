import traceback

from lewis.adapters.stream import Cmd, StreamInterface
from lewis.utils.command_builder import string_arg
from lewis.utils.replies import conditional_reply

NUM_MIN_MAX = "([\-0-9.]+|MAX|MIN)"

if_connected = conditional_reply("connected")


class AG33220AStreamInterface(StreamInterface):
    commands = {
        Cmd("get_amplitude", "^VOLT\?$"),
        Cmd("set_amplitude", "^VOLT " + NUM_MIN_MAX, argument_mappings=[string_arg]),
        Cmd("get_frequency", "^FREQ\?$"),
        Cmd("set_frequency", "^FREQ " + NUM_MIN_MAX, argument_mappings=[string_arg]),
        Cmd("get_offset", "^VOLT:OFFS\?$"),
        Cmd("set_offset", "^VOLT:OFFS " + NUM_MIN_MAX, argument_mappings=[string_arg]),
        Cmd("get_units", "^VOLT:UNIT\?$"),
        Cmd("set_units", "^VOLT:UNIT (VPP|VRMS|DBM)$", argument_mappings=[string_arg]),
        Cmd("get_function", "^FUNC\?$"),
        Cmd(
            "set_function",
            "^FUNC (SIN|SQU|RAMP|PULS|NOIS|DC|USER)$",
            argument_mappings=[string_arg],
        ),
        Cmd("get_output", "^OUTP\?$"),
        Cmd("set_output", "^OUTP (ON|OFF)$", argument_mappings=[string_arg]),
        Cmd("get_idn", "^\*IDN\?$"),
        Cmd("get_voltage_high", "^VOLT:HIGH\?$"),
        Cmd(
            "set_voltage_high",
            "^VOLT:HIGH " + NUM_MIN_MAX,
            argument_mappings=[string_arg],
        ),
        Cmd("get_voltage_low", "^VOLT:LOW\?$"),
        Cmd(
            "set_voltage_low",
            "^VOLT:LOW " + NUM_MIN_MAX,
            argument_mappings=[string_arg],
        ),
        Cmd("get_voltage_range_auto", "^VOLT:RANG:AUTO\?$"),
        Cmd(
            "set_voltage_range_auto",
            "^VOLT:RANG:AUTO (OFF|ON|ONCE)$",
            argument_mappings=[string_arg],
        ),
    }

    in_terminator = "\n"
    out_terminator = "\n"

    # Takes in a value and returns a value in the form of x.xxx0000000000Eyy
    def float_output(self, value):
        value = float("%s" % float("%.4g" % float(value)))
        return "{:+.13E}".format(value)

    @if_connected
    def get_amplitude(self):
        return self.float_output(self._device.amplitude)

    @if_connected
    def set_amplitude(self, new_amplitude):
        self._device.set_new_amplitude(new_amplitude)

    @if_connected
    def get_frequency(self):
        return self.float_output(self._device.frequency)

    @if_connected
    def set_frequency(self, new_frequency):
        self._device.set_new_frequency(new_frequency)

    @if_connected
    def get_offset(self):
        return self.float_output(self._device.offset)

    @if_connected
    def set_offset(self, new_offset):
        self._device.set_offs_and_update_voltage(new_offset)

    @if_connected
    def get_units(self):
        return self._device.units

    @if_connected
    def set_units(self, new_units):
        self._device.units = new_units

    @if_connected
    def get_function(self):
        return self._device.function

    @if_connected
    def set_function(self, new_function):
        self._device.set_function(new_function)

    @if_connected
    def get_output(self):
        return self._device.get_output()

    @if_connected
    def set_output(self, new_output):
        self._device.output = new_output

    @if_connected
    def get_idn(self):
        return self._device.idn

    @if_connected
    def get_voltage_high(self):
        return self.float_output(self._device.voltage_high)

    @if_connected
    def set_voltage_high(self, new_voltage_high):
        self._device.set_new_voltage_high(new_voltage_high)

    @if_connected
    def get_voltage_low(self):
        return self.float_output(self._device.voltage_low)

    @if_connected
    def set_voltage_low(self, new_voltage_low):
        self._device.set_new_voltage_low(new_voltage_low)

    @if_connected
    def get_voltage_range_auto(self):
        return self._device.get_range_auto()

    @if_connected
    def set_voltage_range_auto(self, range_auto):
        self._device.range_auto = range_auto

    def handle_error(self, request, error):
        print(traceback.format_exc())
