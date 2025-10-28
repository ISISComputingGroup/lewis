import logging
from typing import Callable, Concatenate, ParamSpec, Protocol, TypeVar

from lewis.devices.eurotherm import SimulatedEurotherm

from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.byte_conversions import BYTE, int_to_raw_bytes
from lewis.utils.replies import conditional_reply

sensor = "01"


class HasLog(Protocol):
    log: logging.Logger


P = ParamSpec("P")
T = TypeVar("T")
T_self = TypeVar("T_self", bound=HasLog)


def log_replies(f: Callable[Concatenate[T_self, P], T]) -> Callable[Concatenate[T_self, P], T]:
    def _wrapper(self: T_self, *args: P.args, **kwargs: P.kwargs) -> T:
        result = f(self, *args, **kwargs)
        self.log.info(f"Reply in {f.__name__}: {result}")
        return result

    return _wrapper


def bytes_to_int(bytes: bytes) -> int:
    return int.from_bytes(bytes, byteorder="big", signed=True)


def crc16(data: bytes) -> bytes:
    """
    CRC algorithm - translated from section 3-5 of eurotherm manual.
    :param data: the data to checksum
    :return: the checksum
    """
    crc = 0xFFFF

    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1

            crc %= BYTE**2

    return int_to_raw_bytes(crc, 2, low_byte_first=True)


@has_log
class EurothermModbusInterface(StreamInterface):
    """
    This implements the modbus stream interface for a eurotherm.

    Note: Eurotherm uses modbus RTU, not TCP, so cannot use lewis' normal modbus
    implementation here.
    """

    commands = {
        Cmd("any_command", r"^([\s\S]*)$", return_mapping=lambda x: x),
    }

    def __init__(self) -> None:
        super().__init__()
        self.device: SimulatedEurotherm
        self.log: logging.Logger
        # Modbus addresses for the needle valve were obtained from Jamie,
        # full info can be found on the manuals share
        self.read_commands = {
            1: self.get_temperature,
            2: self.get_temperature_sp,
            6: self.get_p,
            8: self.get_i,
            9: self.get_d,
            111: self.get_high_lim,
            112: self.get_low_lim,
            270: self.get_autotune,
            30: self.get_max_output,
            37: self.get_output_rate,
            3: self.get_output,
            1025: self.get_nv_flow,
            1509: self.get_nv_manual_flow,
            1300: self.get_nv_flow_sp_mode,
            4827: self.get_nv_direction,
            1135: self.get_nv_flow_high_lim,
            1136: self.get_nv_flow_low_lim,
            4963: self.get_nv_min_auto_flow_bl_temp,
            4965: self.get_nv_auto_flow_scale,
            1292: self.get_nv_stop,
        }

        self.write_commands = {
            2: self.set_temperature_sp,
            6: self.set_p,
            8: self.set_i,
            9: self.set_d,
            30: self.set_max_output,
            37: self.set_output_rate,
            270: self.set_autotune,
            1509: self.set_nv_manual_flow,
            1300: self.set_nv_flow_sp_mode,
            1135: self.set_nv_flow_high_lim,
            1136: self.set_nv_flow_low_lim,
            4963: self.set_nv_min_auto_flow_bl_temp,
            4965: self.set_nv_auto_flow_scale,
            1292: self.set_nv_stop,
        }

    in_terminator = ""
    out_terminator = ""
    readtimeout = 10

    protocol = "eurotherm_modbus"

    def handle_error(self, request: bytes, error: BaseException | str) -> None:
        error_message = "An error occurred at request " + repr(request) + ": " + repr(error)
        print(error_message)
        self.log.error(error_message)

    @log_replies
    @conditional_reply("connected")
    def any_command(self, command: bytes) -> bytes | None:
        self.log.info(command)
        comms_address = command[0]
        function_code = int(command[1])
        data = command[2:-2]

        assert crc16(command) == b"\x00\x00", "Invalid checksum from IOC"

        if len(data) != 4:
            raise ValueError(f"Invalid message length {len(data)}")

        if function_code == 3:
            return self.handle_read(comms_address, data)
        elif function_code == 6:
            return self.handle_write(data, command)
        else:
            raise ValueError(f"Unknown modbus function code: {function_code}")

    def handle_read(self, comms_address: int, data: bytes) -> bytes:
        mem_address = bytes_to_int(data[0:2])
        words_to_read = bytes_to_int(data[2:4])
        self.log.info(f"Attempting to read {words_to_read} words from mem address: {mem_address}")
        reply_data = self.read_commands[mem_address]()

        self.log.info(f"reply_data = {reply_data}")
        assert -0x8000 <= reply_data <= 0x7FFF, f"reply {reply_data} was outside modbus range, bug?"

        reply = (
            comms_address.to_bytes(1, byteorder="big", signed=True)
            + b"\x03\x02"
            + reply_data.to_bytes(2, byteorder="big", signed=True)
        )

        return reply + crc16(reply)

    def handle_write(self, data: bytes, command: bytes) -> bytes | None:
        mem_address = bytes_to_int(data[0:2])
        value = bytes_to_int(data[2:4])
        self.log.info(f"Attempting to write {value} to mem address: {mem_address}")
        try:
            self.write_commands[mem_address](value)
        except Exception as e:
            self.log.error(e)
            return None
        # On write, device echos command back to IOC
        return command

    def get_temperature(self) -> int:
        return int(self.device.current_temperature(sensor) * self.device.scaling(sensor))

    def get_temperature_sp(self) -> int:
        return int(self.device.ramp_setpoint_temperature(sensor) * self.device.scaling(sensor))

    def set_temperature_sp(self, value: int) -> None:
        self.device.set_ramp_setpoint_temperature(sensor, (value / self.device.scaling(sensor)))

    def get_p(self) -> int:
        return int(self.device.p(sensor))

    def get_i(self) -> int:
        return int(self.device.i(sensor))

    def get_d(self) -> int:
        return int(self.device.d(sensor))

    def set_p(self, value: int) -> None:
        self.device.set_p(sensor, value)

    def set_i(self, value: int) -> None:
        self.device.set_i(sensor, value)

    def set_d(self, value: int) -> None:
        self.device.set_d(sensor, value)

    def get_high_lim(self) -> int:
        return int(self.device.high_lim(sensor) * self.device.scaling(sensor))

    def get_low_lim(self) -> int:
        return int(self.device.low_lim(sensor) * self.device.scaling(sensor))

    def get_autotune(self) -> int:
        return int(self.device.autotune(sensor))

    def set_autotune(self, value: int) -> None:
        self.device.set_autotune(sensor, value)

    def get_max_output(self) -> int:
        return int(self.device.max_output(sensor) * self.device.scaling(sensor))

    def set_max_output(self, value: int) -> None:
        self.device.set_max_output(sensor, (value / self.device.scaling(sensor)))

    def get_output_rate(self) -> int:
        return int(self.device.output_rate(sensor))

    def set_output_rate(self, value: int) -> None:
        self.device.set_output_rate(sensor, value)

    def get_output(self) -> int:
        return int(self.device.output(sensor) * self.device.scaling(sensor))

    def get_nv_flow(self) -> int:
        return int(self.device.needlevalve_flow(sensor))

    def get_nv_manual_flow(self) -> int:
        return int(self.device.needlevalve_manual_flow(sensor))

    def set_nv_manual_flow(self, value: int) -> None:
        self.device.set_needlevalve_manual_flow(sensor, value)

    def get_nv_flow_low_lim(self) -> int:
        return int(self.device.needlevalve_flow_low_lim(sensor))

    def set_nv_flow_low_lim(self, value: int) -> None:
        self.device.set_needlevalve_flow_low_lim(sensor, value)

    def get_nv_flow_high_lim(self) -> int:
        return int(self.device.needlevalve_flow_high_lim(sensor))

    def set_nv_flow_high_lim(self, value: int) -> None:
        self.device.set_needlevalve_flow_high_lim(sensor, value)

    def get_nv_min_auto_flow_bl_temp(self) -> int:
        return int(self.device.needlevalve_min_auto_flow_bl_temp(sensor))

    def set_nv_min_auto_flow_bl_temp(self, value: int) -> None:
        self.device.set_needlevalve_min_auto_flow_bl_temp(sensor, value)

    def get_nv_auto_flow_scale(self) -> int:
        return int(self.device.needlevalve_auto_flow_scale(sensor))

    def set_nv_auto_flow_scale(self, value: int) -> None:
        self.device.set_needlevalve_auto_flow_scale(sensor, value)

    def get_nv_flow_sp_mode(self) -> int:
        return int(self.device.needlevalve_flow_sp_mode(sensor))

    def set_nv_flow_sp_mode(self, value: int) -> None:
        self.device.set_needlevalve_flow_sp_mode(sensor, value)

    def get_nv_direction(self) -> int:
        return int(self.device.needlevalve_direction(sensor))

    def set_nv_stop(self, value: int) -> None:
        self.device.set_needlevalve_stop(sensor, value)

    def get_nv_stop(self) -> int:
        return int(self.device.needlevalve_stop(sensor))
