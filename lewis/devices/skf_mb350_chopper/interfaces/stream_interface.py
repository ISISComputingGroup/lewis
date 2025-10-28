from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.byte_conversions import raw_bytes_to_int

from .crc16 import crc16, crc16_matches
from .response_utilities import (
    general_status_response_packet,
    phase_information_response_packet,
    phase_time_response_packet,
    rotator_angle_response_packet,
)


@has_log
class SkfMb350ChopperStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation. Match anything!
    commands = {
        Cmd("any_command", r"^([\s\S]*)$", return_mapping=lambda x: x),
    }

    in_terminator = "\r\n"
    out_terminator = b""

    def handle_error(self, request, error):
        error_message = (
            "An error occurred at request " + repr(request) + ": " + repr(error)
        )
        print(error_message)
        self.log.error(error_message)
        return str(error)

    def any_command(self, command):
        command_mapping = {
            0x20: self.start,
            0x30: self.stop,
            0x60: self.set_rotational_speed,
            0x81: self.get_rotator_angle,
            0x82: self.set_rotator_angle,
            0x85: self.get_phase_delay,
            0x8E: self.set_gate_width,
            0x90: self.set_nominal_phase,
            0xC0: self.get_phase_info,
        }

        address = command[0]
        if not 0 <= address < 16:
            raise ValueError("Address should be in range 0-15")

        # Constant function code. Should always be 0x80
        if command[1] != 0x80:
            raise ValueError("Function code should always be 0x80")

        command_number = command[2]
        if command_number not in command_mapping.keys():
            raise ValueError("Command number should be in map")

        command_data = [c for c in command[3:-2]]

        if not crc16_matches(command[:-2], command[-2:]):
            raise ValueError(
                "CRC Checksum didn't match. Expected {} but got {}".format(
                    crc16(command[:-2]), command[-2:]
                )
            )

        return command_mapping[command_number](address, command_data)

    def start(self, address, data):
        self._device.start()
        return general_status_response_packet(address, self.device, 0x20)

    def stop(self, address, data):
        self._device.stop()
        return general_status_response_packet(address, self.device, 0x30)

    def set_nominal_phase(self, address, data):
        self.log.info("Setting phase")
        self.log.info("Data = {}".format(data))
        nominal_phase = raw_bytes_to_int(data) / 1000.0
        self.log.info("Setting nominal phase to {}".format(nominal_phase))
        self._device.set_nominal_phase(nominal_phase)
        return general_status_response_packet(address, self.device, 0x90)

    def set_gate_width(self, address, data):
        self.log.info("Setting gate width")
        self.log.info("Data = {}".format(data))
        width = raw_bytes_to_int(data)
        self.log.info("Setting gate width to {}".format(width))
        self._device.set_phase_repeatability(width / 10.0)
        return general_status_response_packet(address, self.device, 0x8E)

    def set_rotational_speed(self, address, data):
        self.log.info("Setting frequency")
        self.log.info("Data = {}".format(data))
        freq = raw_bytes_to_int(data)
        self.log.info("Setting frequency to {}".format(freq))
        self._device.set_frequency(freq)
        return general_status_response_packet(address, self.device, 0x60)

    def set_rotator_angle(self, address, data):
        self.log.info("Setting rotator angle")
        self.log.info("Data = {}".format(data))
        angle_times_ten = raw_bytes_to_int(data)
        self.log.info("Setting rotator angle to {}".format(angle_times_ten / 10.0))
        self._device.set_rotator_angle(angle_times_ten / 10.0)
        return general_status_response_packet(address, self.device, 0x82)

    def get_phase_info(self, address, data):
        self.log.info("Getting phase info")
        return phase_information_response_packet(address, self._device)

    def get_rotator_angle(self, address, data):
        self.log.info("Getting rotator angle")
        return rotator_angle_response_packet(address, self._device)

    def get_phase_delay(self, address, data):
        self.log.info("Getting phase time")
        return phase_time_response_packet(address, self._device)
