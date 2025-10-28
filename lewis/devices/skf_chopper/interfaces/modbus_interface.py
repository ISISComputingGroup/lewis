from os import urandom

from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.byte_conversions import (
    float_to_raw_bytes,
    int_to_raw_bytes,
    raw_bytes_to_int,
)
from lewis.utils.replies import conditional_reply


def log_replies(f):
    def _wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        self.log.info(f"Reply in {f.__name__}: {result}")
        return result

    return _wrapper


@has_log
class SKFChopperModbusInterface(StreamInterface):
    """This implements the modbus stream interface for an skf chopper.
    This is not a full implementation of the device and just handles frequency for now to check
    that modbus comms work OK.
    """

    commands = {
        Cmd("any_command", r"^([\s\S]*)$", return_mapping=lambda x: x),
    }

    def __init__(self):
        super().__init__()
        self.read_commands = {
            353: self.get_freq,  # RBV
            345: self.get_freq,  # SP:RBV
            905: self.get_v13_norm,
            906: self.get_w13_norm,
            907: self.get_v24_norm,
            908: self.get_w24_norm,
            909: self.get_z12_norm,
            910: self.get_v13_fsv,
            911: self.get_w13_fsv,
            912: self.get_v24_fsv,
            913: self.get_w24_fsv,
            914: self.get_z12_fsv,
        }

        self.write_commands = {
            345: self.set_freq,  # SP
        }

    in_terminator = ""
    out_terminator = b""
    protocol = "stream"

    def handle_error(self, request, error):
        error_message = "An error occurred at request " + repr(request) + ": " + repr(error)
        print(error_message)
        self.log.error(error_message)
        return str(error).encode("utf-8")

    @log_replies
    @conditional_reply("connected")
    def any_command(self, command):
        self.log.info(command)
        transaction_id = command[0:2] if self.device.send_ok_transid else urandom(2)
        protocol_id = command[2:4]
        length = int.from_bytes(command[4:6], "big")
        unit = command[6]
        function_code = int(command[7])
        data = command[8:]

        if len(command[6:]) != length:
            raise ValueError(f"Invalid message length, expected {length} but got {len(data)}")

        if function_code == 3:
            return self.handle_read(transaction_id, protocol_id, unit, function_code, data)
        elif function_code == 16:
            return self.handle_write(command, data)
        else:
            raise ValueError(f"Unknown modbus function code: {function_code}")

    def handle_read(self, transaction_id, protocol_id, unit, function_code, data):
        mem_address = raw_bytes_to_int(data[0:2], False)
        words_to_read = raw_bytes_to_int(data[2:4], False)
        self.log.info(f"Attempting to read {words_to_read} words from mem address: {mem_address}")
        if mem_address in self.read_commands.keys():
            reply_data = self.read_commands[mem_address]()
        else:
            reply_data = 0

        self.log.info(f"reply_data = {reply_data}")

        if isinstance(reply_data, float) and words_to_read == 2:
            data_length = 4
            littleendian_bytes = bytearray(float_to_raw_bytes(reply_data, low_byte_first=True))
            # split up in 2-byte words, then swap endianness respectively to big endian.
            # The device represents float32s in 2 words, little endian, but each of these words respectively are big endian.

            # Get the first 2 bytes, then flip endianness
            first_word = littleendian_bytes[:2][::-1]

            # Do the same for the remainder
            second_word = littleendian_bytes[2:][::-1]

            # Concatenate the two bytes/words
            reply_data_bytes = first_word + second_word
        elif isinstance(reply_data, int):
            if words_to_read == 2:
                data_length = 4
                littleendian_bytes = bytearray(
                    int_to_raw_bytes(reply_data, data_length, low_byte_first=True)
                )
                first_word = littleendian_bytes[:2][::-1]
                second_word = littleendian_bytes[2:][::-1]
                reply_data_bytes = first_word + second_word
            else:
                data_length = 2
                reply_data_bytes = int_to_raw_bytes(reply_data, data_length, low_byte_first=False)
        else:
            raise ValueError("Unknown data type or data length")

        function_code_bytes = function_code.to_bytes(1, byteorder="big")
        unit_bytes = unit.to_bytes(1, byteorder="big")
        data_length_bytes = data_length.to_bytes(1, byteorder="big")
        length = int(3 + data_length).to_bytes(2, byteorder="big")

        reply = (
            transaction_id
            + protocol_id
            + length
            + unit_bytes
            + function_code_bytes
            + data_length_bytes
            + reply_data_bytes
        )

        return reply

    def handle_write(self, command, data):
        mem_address = raw_bytes_to_int(data[0:2], False)
        value = raw_bytes_to_int(data[2:4], False)
        self.write_commands[mem_address](value)
        return command

    def get_freq(self):
        return float(self.device.freq)

    def get_v13_norm(self):
        return self.device.v13_norm

    def get_w13_norm(self):
        return self.device.w13_norm

    def get_v24_norm(self):
        return self.device.v24_norm

    def get_w24_norm(self):
        return self.device.w24_norm

    def get_z12_norm(self):
        return self.device.z12_norm

    def get_v13_fsv(self):
        return self.device.v13_fsv

    def get_w13_fsv(self):
        return self.device.w13_fsv

    def get_v24_fsv(self):
        return self.device.v24_fsv

    def get_w24_fsv(self):
        return self.device.w24_fsv

    def get_z12_fsv(self):
        return self.device.z12_fsv

    def set_freq(self, value):
        self.device.freq = value
