import struct
import threading

from lewis.adapters.stream import StreamInterface

EXPECTED_MESSAGE_LENGTH = 188


class MecfrfStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation (No commands - the device always sends a stream of
    # information to the IOC without being polled)
    commands = {}

    in_terminator = ""
    out_terminator = b""

    def __init__(self):
        super(MecfrfStreamInterface, self).__init__()
        self._queue_next_unsolicited_message()

    def _queue_next_unsolicited_message(self):
        timer = threading.Timer(1.0, self.get_data_unsolicited)
        timer.daemon = True
        timer.start()

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
        return str(error)

    def get_data_unsolicited(self):
        self._queue_next_unsolicited_message()

        if not self.device.connected:
            return

        try:
            handler = self.handler
        except AttributeError:
            # Happens if no client is currently connected.
            return
        else:
            if self.device.corrupted_messages:
                # Nonsense message which should cause alarms in the IOC.
                handler.unsolicited_reply(b"A" * EXPECTED_MESSAGE_LENGTH)
            else:
                handler.unsolicited_reply(self._construct_status_message())

    def _construct_status_message(self):
        # Fixed message "preamble"
        msg = b"DATA"

        # There are 6 integer header fields which we ignore. They are:
        # - Order number
        # - Serial number
        # - Length of measurement data
        # - Length of video data
        # - Frame number
        # - Counter
        for _ in range(6):
            msg += struct.pack("L", 0)

        # Two little-endian signed integers corresponding to the data for sensors 1 and 2 respectively.
        msg += struct.pack("<l", int(self.device.sensor1))
        msg += struct.pack("<l", int(self.device.sensor2))

        # 38 more integers corresponding to video data (???), which we ignore.
        for _ in range(38):
            msg += struct.pack("L", 0)

        assert (
            len(msg) == EXPECTED_MESSAGE_LENGTH
        ), "Message length {} was expected to be {}".format(len(msg), EXPECTED_MESSAGE_LENGTH)

        return msg
