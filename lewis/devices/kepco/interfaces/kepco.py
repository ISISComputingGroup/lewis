from functools import wraps

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


def needs_remote_mode(func):
    wraps(func)

    def _wrapper(self, *args, **kwargs):
        if not self._device.remote_comms_enabled:
            raise ValueError("Not in remote mode")
        return func(self, *args, **kwargs)

    return _wrapper


@has_log
class KepcoStreamInterface(StreamInterface):
    in_terminator = "\n"
    out_terminator = "\r\n"

    commands = {
        CmdBuilder("write_voltage").escape("VOLT ").float().build(),
        CmdBuilder("read_actual_voltage").escape("MEAS:VOLT?").build(),
        CmdBuilder("read_actual_current").escape("MEAS:CURR?").build(),
        CmdBuilder("write_current").escape("CURR ").float().build(),
        CmdBuilder("read_setpoint_voltage").escape("VOLT?").build(),
        CmdBuilder("read_setpoint_current").escape("CURR?").build(),
        CmdBuilder("set_output_mode").escape("FUNC:MODE ").arg("VOLT|CURR").build(),
        CmdBuilder("read_output_mode").escape("FUNC:MODE?").build(),
        CmdBuilder("read_output_status").escape("OUTP?").build(),
        CmdBuilder("set_output_status").escape("OUTP ").arg("0|1").build(),
        CmdBuilder("get_IDN").escape("*IDN?").build(),
        CmdBuilder("set_control_mode").escape("SYST:REM ").arg("0|1").build(),
        CmdBuilder("reset").escape("*RST").build(),
        CmdBuilder("get_current_range").escape("CURR:RANG?").build(),
        CmdBuilder("get_voltage_range").escape("VOLT:RANG?").build(),
        CmdBuilder("set_current_range").escape("CURR:RANG ").int().build(),
        CmdBuilder("set_voltage_range").escape("VOLT:RANG ").int().build(),
        CmdBuilder("set_auto_current_range").escape("CURR:RANG:AUTO ").int().build(),
        CmdBuilder("set_auto_voltage_range").escape("VOLT:RANG:AUTO ").int().build(),
    }

    def handle_error(self, request, error):
        self.log.error("An error occurred at request" + repr(request) + ": " + repr(error))
        print("An error occurred at request" + repr(request) + ": " + repr(error))

    @if_connected
    def read_actual_voltage(self):
        return "{0}".format(self._device.voltage)

    @if_connected
    def read_actual_current(self):
        return "{0}".format(self._device.current)

    @if_connected
    @needs_remote_mode
    def write_voltage(self, voltage):
        self._device.setpoint_voltage = voltage

    @if_connected
    @needs_remote_mode
    def write_current(self, current):
        self._device.setpoint_current = current

    @if_connected
    def read_setpoint_voltage(self):
        return "{0}".format(self._device.setpoint_voltage)

    @if_connected
    def read_setpoint_current(self):
        return "{0}".format(self._device.setpoint_current)

    @if_connected
    @needs_remote_mode
    def set_output_mode(self, mode):
        self._device.output_mode = 0 if mode.startswith("VOLT") else 1

    @if_connected
    def read_output_mode(self):
        return "{0}".format(self._device.output_mode)

    @if_connected
    @needs_remote_mode
    def set_output_status(self, status):
        self._device.output_status = status

    @if_connected
    def read_output_status(self):
        return "{0}".format(self._device.output_status)

    @if_connected
    def get_IDN(self):
        return "{0}".format(self._device.idn)

    @if_connected
    def set_control_mode(self, mode):
        if self._device.firmware <= 2.0:
            raise ValueError("No SYST:REM command available")
        else:
            mode = int(mode)
            if mode not in [0, 1]:
                raise ValueError("Invalid mode in set_control_mode: {}".format(mode))
            self._device.remote_comms_enabled = mode == 1

    @if_connected
    def reset(self):
        self._device.reset()

    @if_connected
    def get_current_range(self):
        return f"{self._device.current_range}"

    @if_connected
    def get_voltage_range(self):
        return f"{self._device.voltage_range}"

    @if_connected
    def set_current_range(self, range):
        if range == 1 or range == 4:
            self._device.current_range = range
        else:
            raise ValueError(f"Invalid current range {range}")

    @if_connected
    def set_voltage_range(self, range):
        if range == 1 or range == 4:
            self._device.voltage_range = range
        else:
            raise ValueError(f"Invalid voltage range {range}")

    @if_connected
    def set_auto_current_range(self, range):
        if range == 0 or range == 1:
            self._device.auto_current_range = range
        else:
            raise ValueError(f"Invalid auto current range {range}")

    @if_connected
    def set_auto_voltage_range(self, range):
        if range == 0 or range == 1:
            self._device.auto_voltage_range = range
        else:
            raise ValueError(f"Invalid auto voltage range {range}")
