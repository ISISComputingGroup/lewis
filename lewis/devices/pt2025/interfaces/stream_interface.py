import threading

from lewis.adapters.stream import StreamInterface
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")
DATA = "L12.123456T"
NUMBER_OF_MESSAGES = 10


class Pt2025StreamInterface(StreamInterface):
    commands = {}
    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def __init__(self):
        super(Pt2025StreamInterface, self).__init__()
        self._queue_next_unsolicited_message()

    def _queue_next_unsolicited_message(self):
        timer = threading.Timer(1.0, self.get_data_unsolicited)
        timer.daemon = True
        timer.start()

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
            handler.unsolicited_reply(str(self.device.data))

    def handle_error(self, request, error):
        pass
