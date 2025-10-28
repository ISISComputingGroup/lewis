from lewis.adapters.stream import Cmd, StreamInterface
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


class FlipprpsStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        Cmd("set_polarity_down", "^dn$"),
        Cmd("set_polarity_up", "^up$"),
        Cmd("get_id", "^id$"),
    }

    in_terminator = "\r\n"
    out_terminator = in_terminator

    @if_connected
    def get_id(self):
        return self._device.id

    @if_connected
    def set_polarity_down(self):
        self._device.polarity = 0
        return "OK"

    @if_connected
    def set_polarity_up(self):
        self._device.polarity = 1
        return "OK"

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
