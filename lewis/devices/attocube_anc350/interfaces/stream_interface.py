from functools import partial

from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.byte_conversions import int_to_raw_bytes, raw_bytes_to_int

BYTES_IN_INT = 4
HEADER_LENGTH = 4 * BYTES_IN_INT

convert_to_response = partial(int_to_raw_bytes, length=BYTES_IN_INT, low_byte_first=True)

# NB, all variables used from here onwards are named the same in the C driver
# 'hump' in the controller refers to hardware limits
UC_SET = 0  # Set command
UC_GET = 1  # Get command
UC_ACK = 3  # Ack command
UC_TELL = 4  # Event command

UC_REASON_OK = 0  # All ok
UC_REASON_ADDR = 1  # Invalid address
UC_REASON_RANGE = 2  # Value out of range
UC_REASON_IGNORED = 3  # Telegram was ignored
UC_REASON_VERIFY = 4  # Verify of data failed
UC_REASON_TYPE = 5  # Wrong type of data
UC_REASON_UNKNW = 99  # unknown error

#  Memory addresses
#  Read
ID_ANC_AMPL = 0x400
ID_ANC_FAST_FREQ = 0x0401
ID_ANC_STATUS = 0x0404
ID_ANC_REFCOUNTER = 0x0407  # The position of home
ID_ANC_COUNTER = 0x0415
ID_ANC_UNIT = 0x041D
ID_ANC_SENSOR_VOLT = 0x0526
ID_ANC_REGSPD_SETP = 0x0542  # Speed of the controller
ID_ANC_REGSPD_SETPS = 0x0549  # Step width of the controller
ID_ANC_MAX_AMP = 0x054F
ID_ANC_CAP_VALUE = 0x0569

#  Write
ID_ANC_STOP_EN = 0x0450  # Enables 'hump' detection
ID_ANC_REGSPD_SELSP = 0x054A  # Type of setpoint for the speed
ID_ANC_TARGET = 0x0408  # The target to move to
ID_ANC_RUN_TARGET = 0x040D  # Actually start the move to target
ID_ANC_AXIS_ON = 0x3030  # Turn the axis on (on power cycle the axis is turned off

# Status bitmask
ANC_STATUS_RUNNING = 0x0001
ANC_STATUS_HUMP = 0x0002
ANC_STATUS_SENS_ERR = 0x0100
ANC_STATUS_DISCONN = 0x0400
ANC_STATUS_REF_VALID = 0x0800
ANC_STATUS_ENABLE = 0x1000


def convert_to_ints(command, start, end):
    """Converts an incoming set of bytes into a list of ints. Assuming there are BYTES_IN_INT bytes in an int.

    Args:
        command: The incoming bytes.
        start: The index at which to start
        end: The index at which to end

    Returns: A list of integers converted from the command.
    """
    return [
        raw_bytes_to_int(command[x : x + BYTES_IN_INT]) for x in range(start, end, BYTES_IN_INT)
    ]


def generate_response(address, index, correlation_num, data=None):
    """Creates a response of the format:
    * Length (the length of the response)
    * Opcode (always ACK in this case)
    * Address (where the driver had read/written to)
    * Index (the axis the driver had read/written from)
    * Correlation Number (the ID of the message we're responding to)
    * Reason (whether the request was successful, always SUCCESS currently)

    Args:
        address: The memory address where the driver had read/written to
        index: The axis the driver had read/written from
        correlation_num: The ID of the message we're responding to
        data (optional): The data we want to send back to the driver (only valid on a get command)

    Returns: The raw bytes to send back to the driver.
    """
    int_responses = [UC_ACK, address, index, correlation_num, UC_REASON_OK]
    if data is not None:
        int_responses.append(data)
    response = bytearray()
    for int_response in int_responses:
        response += convert_to_response(int_response)
    return convert_to_response(len(response)) + response


@has_log
class AttocubeANC350StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation. Match anything!
    commands = {
        Cmd("any_command", r"^([\s\S]*)$", return_mapping=lambda x: x),
    }

    in_terminator = ""
    out_terminator = b""

    # Due to poll rate of the driver this will get individual commands
    readtimeout = 10

    def handle_error(self, request, error):
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))
        return str(error)

    def any_command(self, command):
        response = ""

        if not self.device.connected:
            # Used rather than conditional_reply decorator to improve error message
            raise ValueError("Device simulating disconnection")

        while command:
            # Length doesn't include itself
            length = raw_bytes_to_int(command[:BYTES_IN_INT]) + BYTES_IN_INT

            response += self.handle_single_command(command[:length])

            command = command[length:]

        return response

    def handle_single_command(self, command):
        length = raw_bytes_to_int(command[:BYTES_IN_INT])

        opcode, address, index, correlation_num = convert_to_ints(
            command, BYTES_IN_INT, HEADER_LENGTH + 1
        )

        if length > HEADER_LENGTH:
            # This is probably a set command
            data = convert_to_ints(command, HEADER_LENGTH + BYTES_IN_INT, len(command))

        # Length should describe command minus itself
        if len(command) - BYTES_IN_INT != length:
            raise ValueError(
                "Told I would receive {} bytes but received {}".format(
                    length, len(command) - BYTES_IN_INT
                )
            )

        if opcode == UC_GET:
            return self.get(address, index, correlation_num)
        elif opcode == UC_SET:
            return self.set(address, index, correlation_num, data)
        else:
            raise ValueError("Unrecognised opcode {}".format(opcode))

    def set(self, address, index, correlation_num, data):
        self.log.info("Setting address {} with data {}".format(address, data[0]))
        command_mapping = {
            ID_ANC_TARGET: partial(self.device.set_position_setpoint, position=data[0]),
            ID_ANC_RUN_TARGET: self.device.move,
            ID_ANC_AMPL: partial(self.device.set_amplitude, data[0]),
            ID_ANC_AXIS_ON: partial(self.device.set_axis_on, data[0]),
        }

        try:
            command_mapping[address]()
            print("Device amp is {}".format(self.device.amplitude))
        except KeyError:
            pass  # Ignore unimplemented commands for now
        return generate_response(address, index, correlation_num)

    def get(self, address, index, correlation_num):
        self.log.info("Getting address {}".format(address))
        command_mapping = {
            ID_ANC_COUNTER: int(self.device.position),
            ID_ANC_REFCOUNTER: 0,
            ID_ANC_STATUS: ANC_STATUS_REF_VALID + ANC_STATUS_ENABLE,
            ID_ANC_UNIT: 0x00,
            ID_ANC_REGSPD_SETP: self.device.speed,
            ID_ANC_SENSOR_VOLT: 2000,
            ID_ANC_MAX_AMP: 60000,
            ID_ANC_AMPL: self.device.amplitude,
            ID_ANC_FAST_FREQ: 1000,
        }
        try:
            data = command_mapping[address]
        except KeyError:
            data = 0  # Just return 0 for now
        return generate_response(address, index, correlation_num, data)
