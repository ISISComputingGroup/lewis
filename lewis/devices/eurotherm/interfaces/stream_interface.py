import logging
from typing import Callable, ClassVar, Concatenate, ParamSpec, TypeVar

from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from lewis_emulators.eurotherm import SimulatedEurotherm

if_connected = conditional_reply("connected")

P = ParamSpec("P")
T = TypeVar("T")
T_self = TypeVar("T_self")


def translate_adddress(
    f: Callable[Concatenate[T_self, str, P], T],
) -> Callable[Concatenate[T_self, str, P], T]:
    """Translate the eurotherm address from GAD,GAD,LAD,LAD to GAD,LAD."""

    def wrapper(self: T_self, addr: str, *args: P.args, **kwargs: P.kwargs) -> T:
        addr = str(addr)
        assert len(addr) == 4
        gad = addr[0]
        assert addr[1] == gad
        lad = addr[2]
        assert addr[3] == lad

        address = gad + lad

        return f(self, address, *args, **kwargs)

    return wrapper


class EurothermStreamInterface(StreamInterface):
    """Stream interface for the serial port."""

    def __init__(self) -> None:
        """Create stream interface for serial port Eurotherm sensor."""
        self.device: SimulatedEurotherm
        self.log: logging.Logger

    commands: ClassVar = {
        CmdBuilder("get_current_temperature").eot().arg("[0-9]{4}").escape("PV").enq().build(),
        CmdBuilder("get_setpoint").eot().arg("[0-9]{4}").escape("SL").enq().build(),
        CmdBuilder("get_ramp_setpoint").eot().arg("[0-9]{4}").escape("SP").enq().build(),
        CmdBuilder("get_output").eot().arg("[0-9]{4}").escape("OP").enq().build(),
        CmdBuilder("get_max_output").eot().arg("[0-9]{4}").escape("HO").enq().build(),
        CmdBuilder("get_output_rate").eot().arg("[0-9]{4}").escape("OR").enq().build(),
        CmdBuilder("get_autotune").eot().arg("[0-9]{4}").escape("AT").enq().build(),
        CmdBuilder("get_proportional").eot().arg("[0-9]{4}").escape("XP").enq().build(),
        CmdBuilder("get_derivative").eot().arg("[0-9]{4}").escape("TD").enq().build(),
        CmdBuilder("get_integral").eot().arg("[0-9]{4}").escape("TI").enq().build(),
        CmdBuilder("get_highlim").eot().arg("[0-9]{4}").escape("HS").enq().build(),
        CmdBuilder("get_lowlim").eot().arg("[0-9]{4}").escape("LS").enq().build(),
        CmdBuilder("get_error").eot().arg("[0-9]{4}").escape("EE").enq().build(),
        CmdBuilder("get_address").eot().arg("[0-9]{4}").escape("").enq().build(),
        CmdBuilder("set_ramp_setpoint", arg_sep="")
        .eot()
        .arg("[0-9]{4}")
        .stx()
        .escape("SL")
        .float()
        .etx()
        .any()
        .build(),
        CmdBuilder("set_output_rate", arg_sep="")
        .eot()
        .arg("[0-9]{4}")
        .stx()
        .escape("OR")
        .float()
        .etx()
        .any()
        .build(),
    }

    # Add terminating characters manually for each command,
    # as write and read commands use different formatting for their 'in' commands.
    in_terminator = ""
    out_terminator = ""
    readtimeout = 1

    # calculate a eurotherm xor checksum character from a data string
    def make_checksum(self, chars: str) -> str:
        """Make a checksum to send after a read or write command.

        Args:
            chars: a string holding the read or write command.

        Returns: A unicode string of one value, the checksum of the read
            or write command, in chr type.

        """
        checksum = 0
        for c in chars:
            checksum ^= ord(c)
        return chr(checksum)

    def make_read_reply(self, command: str, value: str | float | int) -> str:
        """Make a read reply to send to Eurotherm sensor.

        Args:
            command: a string which holds the read command to send.
            value: a string/float/int which holds the value one wants to read.

        Returns: A string holding the read reply.

        """
        reply = f"\x02{command}{value!s}\x03"
        # checksum calculated on characters after \x02 but up to and including \x03
        return f"{reply}{self.make_checksum(reply[1:])}"

    def handle_error(self, request: str, error: Exception | str) -> None:
        """Print an error if a command is not recognised.

        Args:
            request: requested string
            error: problem

        Returns: None

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    @if_connected
    @translate_adddress
    def get_address(self, addr: str) -> str:
        """Get the address of the specific Eurotherm sensor, i.e. A01 or 0011.

        Returns: the address as a string.
        """
        return self.make_read_reply("", self.device.address(addr))

    @if_connected
    @translate_adddress
    def get_setpoint(self, addr: str) -> str | None:
        """Get the setpoint of the Eurotherm sensor.

        Returns: the setpoint value formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("SL", self.device.setpoint_temperature(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_proportional(self, addr: str) -> str | None:
        """Get the proportional of the Eurotherm sensor.

        Returns: the proportional value formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("XP", self.device.p(addr))
        except Exception as e:
            print(e)
            return None

    @if_connected
    @translate_adddress
    def get_integral(self, addr: str) -> str | None:
        """Get the integral of the Eurotherm sensor.

        Returns: the integral value formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("TI", self.device.i(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_derivative(self, addr: str) -> str | None:
        """Get the derivative of the Eurotherm sensor.

        Returns: the derivative value formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("TD", self.device.d(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_output(self, addr: str) -> str | None:
        """Get the output of the Eurotherm sensor.

        Returns: the output value formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("OP", self.device.output(addr))
        except Exception as e:
            print(e)
            return None

    @if_connected
    @translate_adddress
    def get_highlim(self, addr: str) -> str | None:
        """Get the high limit of the Eurotherm sensor.

        Returns: the high limit formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("HS", self.device.high_lim(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_lowlim(self, addr: str) -> str | None:
        """Get the low limit of the Eurotherm sensor.

        Returns: the low limit formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("LS", self.device.low_lim(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_max_output(self, addr: str) -> str | None:
        """Get the max output value of the Eurotherm sensor.

        Returns: the max output value formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("HO", self.device.max_output(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_autotune(self, addr: str) -> str | None:
        """Get the autotune value of the Eurotherm sensor.

        Returns: the autotune formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("AT", self.device.autotune(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_current_temperature(self, addr: str) -> str | None:
        """Get the current temperature of the device.

        Returns: the current temperature formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("PV", self.device.current_temperature(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_output_rate(self, addr: str) -> str | None:
        """Get output rate of Eurotherm sensor.

        Returns: the output rate formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("OR", self.device.output_rate(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def set_output_rate(self, addr: str, output_rate: int, _: str) -> str | None:
        """Set the output rate.

        Args:
            output_rate: output rate to set as int.
            _: argument captured by the command.
            addr: address of the Eurotherm sensor.

        """
        try:
            self.device.set_output_rate(addr, output_rate)
            return "\x06"
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_ramp_setpoint(self, addr: str) -> str | None:
        """Get the set point temperature.

        Returns: the current set point temperature formatted like the Eurotherm protocol.
        """
        try:
            return self.make_read_reply("SP", self.device.ramp_setpoint_temperature(addr))
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def set_ramp_setpoint(self, addr: str, temperature: float, _: str) -> str | None:
        """Set the set point temperature.

        Args:
            temperature: the temperature to set the setpoint to.
            _: argument captured by the command.
            addr: address of the Eurotherm sensor.

        """
        try:
            self.device.set_ramp_setpoint_temperature(addr, temperature)
            return "\x06"
        except Exception:
            return None

    @if_connected
    @translate_adddress
    def get_error(self, addr: str) -> str:
        """Get the error.

        Returns: the current error code in HEX.
        """
        reply = "\x02EE>0x{}\x03".format(self.device.error(addr))
        return f"{reply}{self.make_checksum(reply[1:])}"
