from lewis.utils.byte_conversions import float_to_raw_bytes, int_to_raw_bytes

from .crc16 import crc16


def build_interlock_status(device):
    """Builds an integer representation of the interlock bit-field.
    :param device: the lewis device
    :return: int representation of the bit field
    """
    interlocks = device.get_interlocks()

    bit = 1
    result = 0
    for ilk in interlocks.values():
        result += bit if ilk else 0
        bit *= 2

    return result


def build_device_status(device):
    """Builds an integer representation of the device status bit-field.
    :param device: the lewis device
    :return: int representation of the bit field
    """
    status_bits = [
        device.is_controller_ok(),
        device.is_up_to_speed(),
        device.is_able_to_run(),
        device.is_shutting_down(),
        device.is_levitation_complete(),
        device.is_phase_locked(),
        device.get_motor_direction() > 0,
        device.is_avc_on(),
    ]

    bit = 1
    result = 0
    for stat in status_bits:
        result += bit if stat else 0
        bit *= 2
    return result


def general_status_response_packet(address, device, command):
    """Returns the general response packet, the default response to any command that doesn't have a more specific response.

    Response structure is:
        8 bytes common header (see ResponseBuilder.add_common_header)

    :param address: The address of this device
    :param device: The lewis device
    :param command: The command number that this is a reply to
    :return: The response
    """
    return ResponseBuilder().add_common_header(address, command, device).build()


def phase_information_response_packet(address, device):
    """Returns the response to the "get_phase_information" command.

    Response structure is:
        8 bytes common header (see ResponseBuilder.add_common_header)
        4 bytes (IEEE single-precision float): The current phase
        4 bytes (IEEE single-precision float): Phase repeatability
        4 bytes (IEEE single-precision float): Phase percent OK

    :param address: The address of this device
    :param device: The lewis device
    :return: The response
    """
    return (
        ResponseBuilder()
        .add_common_header(address, 0xC0, device)
        .add_float(device.get_phase())
        .add_float(device.get_phase_repeatability())
        .add_float(device.get_phase_percent_ok())
        .build()
    )


def rotator_angle_response_packet(address, device):
    """Returns the response to the "get_rotator_angle" command.

    Response structure is:
        8 bytes common header (see ResponseBuilder.add_common_header)
        4 bytes (unsigned int): The current rotator angle

    :param address: The address of this device
    :param device: The lewis device
    :return: The response
    """
    return (
        ResponseBuilder()
        .add_common_header(address, 0x81, device)
        .add_int(int(device.get_rotator_angle() * 10), 4)
        .build()
    )


def phase_time_response_packet(address, device):
    """Returns the response to the "get_phase_information" command.

    Response structure is:
        8 bytes common header (see ResponseBuilder.add_common_header)
        4 bytes (unsigned int): The current rotator angle

    :param address: The address of this device
    :param device: The lewis device
    :return: The response
    """
    return (
        ResponseBuilder()
        .add_common_header(address, 0x85, device)
        .add_float(device.get_phase() / 1000.0)
        .build()
    )


class ResponseBuilder(object):
    """Response builder which formats the responses as bytes."""

    def __init__(self):
        self.response = bytearray()

    def add_int(self, value, length, low_byte_first=True):
        """Adds an integer to the builder
        :param value: The integer to add
        :param length: How many bytes should the integer be represented as
        :param low_byte_first: If true (default), put the least significant byte first.
                               If false, put the most significant byte first.
        :return: The builder
        """
        self.response += int_to_raw_bytes(value, length, low_byte_first)
        return self

    def add_float(self, value):
        """Adds an float to the builder (4 bytes, IEEE single-precision)
        :param value: The float to add
        :return: The builder
        """
        self.response += float_to_raw_bytes(value)
        return self

    def add_common_header(self, address, command_number, device):
        """Adds the common header.

        The header bytes are as follows:
            1 byte (unsigned int): Device address
            1 byte (unsigned int): Command number
            1 byte (unsigned int): Error status (always zero in the emulator)
            1 byte (bit field): Device status bit-field
            2 bytes (bit field): Device interlock status bit-field
            2 bytes (unsigned int): Current frequency of the chopper in rpm.

        :param address: The address of this device
        :param command_number: The command number that this is a reply to
        :param device: The lewis device
        :return: (ResponseBuilder) the builder with the common header bytes.
        """
        return (
            self.add_int(address, 1)
            .add_int(command_number, 1)
            .add_int(0x00, 1)
            .add_int(build_device_status(device), 1)
            .add_int(build_interlock_status(device), 2, low_byte_first=False)
            .add_int(int(device.get_frequency()), 2)
        )

    def build(self):
        """Gets the response from the builder
        :return: the response
        """
        self.response += crc16(self.response)
        return self.response
