import logging
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from ..utils import RampDirection, RampTarget

if TYPE_CHECKING:
    from ..device import SimulatedCRYOSMS

ON_STATES = ["ON", "1"]
OFF_STATES = ["OFF", "0"]


if_connected = conditional_reply("connected")


@has_log
class CRYOSMSStreamInterface(StreamInterface):
    in_terminator = "\r\n"
    out_terminator = ""

    def __init__(self) -> None:
        self.log: logging.Logger
        self._device: SimulatedCRYOSMS

        # Set regex for shorthand or longhand with 0 or more leading and trailing spaces
        re_set = " *S(?:ET)* *"
        re_get = " *G(?:ET)* *"  # Get regex
        self.commands = {
            # Get commands
            CmdBuilder(self.read_direction).regex(re_get).regex("S(?:IGN)*").spaces().eos().build(),
            CmdBuilder(self.read_output_mode).spaces().regex("T(?:ESLA)*").spaces().eos().build(),
            CmdBuilder(self.read_output).regex(re_get).regex("O(?:UTPUT)*").spaces().eos().build(),
            CmdBuilder(self.read_ramp_status)
            .spaces()
            .regex("R(?:AMP)*")
            .spaces()
            .regex("S(?:TATUS)*")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.read_heater_status)
            .spaces()
            .regex("H(?:EATER)*")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.read_max_target)
            .regex(re_get)
            .regex("(?:MAX|!)*")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.read_mid_target)
            .regex(re_get)
            .regex("(?:MID|%)*")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.read_ramp_rate).regex(re_get).regex("R(?:ATE)*").spaces().eos().build(),
            CmdBuilder(self.read_limit).regex(re_get).regex("V(?:L)*").spaces().eos().build(),
            CmdBuilder(self.read_pause).spaces().regex("P(?:AUSE)*").spaces().eos().build(),
            CmdBuilder(self.read_heater_value)
            .regex(re_get)
            .regex("H(?:V)*")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.read_constant).regex(re_get).regex("T(?:PA)").spaces().eos().build(),
            # Set commands
            CmdBuilder(self.write_direction)
            .spaces()
            .regex("D(?:IRECTION)*")
            .spaces()
            .arg(r"0|-|\+")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_output_mode)
            .spaces()
            .regex("T(?:ESLA)*")
            .spaces()
            .arg("OFF|ON|0|1")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_ramp_target)
            .spaces()
            .regex("R(?:AMP)*")
            .spaces()
            .arg("ZERO|MID|MAX|0|%|!")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_heater_status)
            .spaces()
            .regex("H(?:EATER)*")
            .spaces()
            .arg("OFF|ON|1|0")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_pause)
            .spaces()
            .regex("P(?:AUSE)*")
            .spaces()
            .arg("OFF|ON|0|1")
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_heater_value)
            .regex(re_set)
            .regex("H(?:EATER)*")
            .spaces()
            .float()
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_max_target)
            .regex(re_set)
            .regex("(?:MAX|!)")
            .spaces()
            .float()
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_mid_target)
            .regex(re_set)
            .regex("(?:MID|%)")
            .spaces()
            .float()
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_ramp_rate)
            .regex(re_set)
            .regex("R(?:AMP)*")
            .spaces()
            .float()
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_limit)
            .regex(re_set)
            .regex("L(?:IMIT)*")
            .spaces()
            .float()
            .spaces()
            .eos()
            .build(),
            CmdBuilder(self.write_constant)
            .regex(re_set)
            .regex("T(?:PA)*")
            .spaces()
            .float()
            .spaces()
            .eos()
            .build(),
        }

    def _out_message(self, message: str, terminator: str = "\r\n\x13") -> str:
        return "........ {}{}".format(message, terminator)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _create_log_message(self, pv: str, value: float | int | str, suffix: str = "") -> None:
        current_time = self._timestamp()
        self._device.log_message = "{} {}: {}{}".format(current_time, pv, value, suffix)

    def handle_error(self, request: str, error: str | BaseException) -> None:
        self.log.error("Error occurred at {}: {}".format(request, error))

    def _get_output_mode_string(self) -> str:
        return "TESLA" if self._device.is_output_mode_tesla else "AMPS"

    def _get_paused_state_str(self) -> str:
        return "ON" if self._device.is_paused else "OFF"

    def _get_ramp_target_value(self) -> float:
        if self._device.ramp_target.name == "MID":
            return self._device.mid_target
        elif self._device.ramp_target.name == "MAX":
            return self._device.max_target
        elif self._device.ramp_target.name == "ZERO":
            return self._device.zero_target
        raise RuntimeError("Unknown ramp target {}".format(self._device.ramp_target.name))

    @if_connected
    def read_direction(self) -> str:
        return "........ CURRENT DIRECTION: {}\r\n\x13".format(self._device.direction.name)

    @if_connected
    def write_direction(self, direction: Literal["+"] | Literal["-"] | Literal["0"]) -> str:
        if direction == "+":
            self._device.direction = RampDirection.POSITIVE
        if direction == "-":
            self._device.direction = RampDirection.NEGATIVE
        if direction == "0":
            self._device.direction = RampDirection.ZERO
        return "\x13"

    @if_connected
    def read_output_mode(self) -> str:
        return self._out_message("UNITS: {}\r\n\x13".format(self._get_output_mode_string()))

    @if_connected
    def read_output(self) -> str:
        sign = -1 if self._device.direction == RampDirection.NEGATIVE else 1
        return "........ OUTPUT: {} {} AT {} VOLTS \r\n\x13".format(
            self._device.output * sign, self._get_output_mode_string(), self._device.output_voltage
        )

    @if_connected
    def write_output_mode(self, output_mode: str) -> str:
        # Convert values if output mode is changing between amps(OFF) / tesla(ON)
        constant = self._device.constant
        if output_mode in ON_STATES:
            self._create_log_message("UNITS", "TESLA")
            if not self._device.is_output_mode_tesla:
                self._device.switch_mode("TESLA")
        elif output_mode in OFF_STATES:
            self._create_log_message("UNITS", "AMPS")
            if constant == 0:
                self._device.error_message = "------> No field constant has been entered"
            else:
                if self._device.is_output_mode_tesla:
                    self._device.switch_mode("AMPS")
        else:
            raise ValueError("Invalid arguments sent")
        return f"{self._device.log_message}\r\n\x13"

    @if_connected
    def read_ramp_target(self) -> str:
        return self._out_message("RAMP TARGET: {}".format(self._device.ramp_target.name))

    @if_connected
    def read_ramp_status(self) -> str:
        output = self._device.output
        status_message = "RAMP STATUS: "
        if self._device.is_paused:
            status_message += "HOLDING ON PAUSE AT {} {}".format(
                output, self._get_output_mode_string()
            )
        elif self._device.at_target:
            status_message += "HOLDING ON TARGET AT {} {}".format(
                output, self._get_output_mode_string()
            )
        elif self._device.is_quenched:
            status_message += "QUENCH TRIP AT {} {}".format(output, self._get_output_mode_string())
        elif self._device.is_xtripped:
            status_message += "EXTERNAL TRIP AT {} {}".format(
                output, self._get_output_mode_string()
            )
        elif not self._device.at_target and not self._device.is_paused:
            status_message += "RAMPING FROM {} TO {} {} AT {:07.5f} A/SEC".format(
                self._device.prev_target,
                self._device.mid_target,
                self._get_output_mode_string(),
                self._device.ramp_rate,
            )
        else:
            raise ValueError("Didn't match any of the expected conditions")
        return self._out_message(status_message)

    @if_connected
    def write_ramp_target(self, ramp_target_str: str) -> None:
        if ramp_target_str in ["0", "ZERO"]:
            ramp_target = RampTarget.ZERO
        elif ramp_target_str in ["%", "MID"]:
            ramp_target = RampTarget.MID
        elif ramp_target_str in ["!", "MAX"]:
            ramp_target = RampTarget.MAX
        else:
            raise ValueError("Invalid arguments sent")
        self._device.ramp_target = ramp_target
        self._device.is_paused = False

    @if_connected
    def read_ramp_rate(self) -> str:
        return self._out_message("RAMP RATE: {} A/SEC".format(self._device.ramp_rate))

    @if_connected
    def write_ramp_rate(self, ramp_rate: int | float | str) -> str:
        self._device.ramp_rate = float(ramp_rate)
        self._create_log_message("RAMP RATE", ramp_rate, suffix=" A/SEC")
        return f"{self._device.log_message}\r\n\x13"

    @if_connected
    def read_heater_status(self) -> str:
        heater_value = "ON" if self._device.is_heater_on else "OFF"
        if self._device.output_persist != 0.0 and heater_value == "OFF":
            return self._out_message(
                "HEATER STATUS: SWITCHED OFF AT {} {}".format(
                    self._device.output_persist, self._get_output_mode_string()
                )
            )
        else:
            return self._out_message("HEATER STATUS: {}".format(heater_value))

    @if_connected
    def write_heater_status(self, heater_status: str) -> str:
        if heater_status in ON_STATES:
            self._device.output_persist = 0.0
            self._device.is_heater_on = True
        elif heater_status in OFF_STATES:
            self._device.output_persist = self._device.output
            self._device.is_heater_on = False
        else:
            raise ValueError("Invalid arguments sent")
        self._create_log_message("HEATER STATUS", heater_status)
        return self._out_message(f"HEATER STATUS: {heater_status}")

    @if_connected
    def read_pause(self) -> str:
        return self._out_message("PAUSE STATUS: {}".format(self._get_paused_state_str()))

    @if_connected
    def write_pause(self, paused: str) -> str:
        mode = self._get_output_mode_string()
        target = self._get_ramp_target_value()
        rate = self._device.ramp_rate
        output = "HOLDING ON PAUSE AT {} {}".format(self._device.output, mode)
        if paused in ON_STATES:
            self._device.is_paused = True
            self._create_log_message("PAUSE STATUS", output)
        elif paused in OFF_STATES:
            self._device.is_paused = False
            if self._device.check_is_at_target():
                self._create_log_message("RAMP STATUS", output)
            else:
                output = (
                    f"RAMPING FROM {self._device.output:.6f} "
                    f"TO {target:.6f} {mode} AT {rate:.6f} A/SEC"
                )
                self._create_log_message("RAMP STATUS", output)
        else:
            raise ValueError("Invalid arguments sent")

        return self._out_message("PAUSE STATUS: {}".format(paused))

    @if_connected
    def read_heater_value(self) -> str:
        return self._out_message("HEATER OUTPUT: {} VOLTS".format(self._device.heater_value))

    @if_connected
    def write_heater_value(self, heater_value: float) -> str:
        self._device.heater_value = heater_value
        self._create_log_message("HEATER OUTPUT", heater_value, suffix=" VOLTS")
        return f"{self._device.log_message}\r\n\x13"

    @if_connected
    def read_max_target(self) -> str:
        mode = self._get_output_mode_string()
        return self._out_message(
            "MAX SETTING: {:.4} {}".format(float(self._device.max_target), mode), terminator="\r\n"
        )

    @if_connected
    def write_max_target(self, max_target: int | float | str) -> str:
        self._device.max_target = abs(float(max_target))  # abs because PSU ignores sign
        units = self._get_output_mode_string()
        self._create_log_message("MAX SETTING", max_target, suffix=" {}".format(units))
        return f"{self._device.log_message}\r\n\x13"

    @if_connected
    def read_mid_target(self) -> str:
        mode = self._get_output_mode_string()
        return self._out_message(
            "MID SETTING: {:.4} {}".format(float(self._device.mid_target), mode),
            terminator="\r\n\x13",
        )

    @if_connected
    def write_mid_target(self, mid_target: int | float | str) -> str:
        self._device.mid_target = abs(float(mid_target))  # abs because PSU ignores sign
        units = self._get_output_mode_string()
        self._create_log_message("MID SETTING", mid_target, suffix=" {}".format(units))
        return f"{self._device.log_message}\r\n\x13"

    @if_connected
    def read_limit(self) -> str:
        return self._out_message("VOLTAGE LIMIT: {} VOLTS".format(self._device.limit))

    @if_connected
    def write_limit(self, limit: float) -> str:
        self._device.limit = limit
        self._create_log_message("VOLTAGE LIMIT", limit, suffix=" VOLTS")
        return f"{self._device.log_message}\r\n\x13"

    @if_connected
    def read_constant(self) -> str:
        return self._out_message("FIELD CONSTANT: {:.7} T/A".format(self._device.constant))

    @if_connected
    def write_constant(self, constant: int | float | str) -> str:
        self._device.constant = float(constant)
        self._create_log_message("FIELD CONSTANT", constant, suffix=" T/A")
        return f"{self._device.log_message}\r\n\x13"
