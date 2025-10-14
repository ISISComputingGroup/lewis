from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


class SmrtmonStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_stat").escape("STAT").build(),
        CmdBuilder("get_oplm").escape("OPLM").build(),
        CmdBuilder("get_lims").escape("LIMS").build(),
    }
    in_terminator = "\r"
    out_terminator = "\r"

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
        return str(error)

    @if_connected
    def get_stat(self):
        # Actual device responds with the device's current time as second-to-last item
        return "{},{},{},{},{},{},{},{},{},{},23:59:59,{}".format(*self._device.stat)

    @if_connected
    def get_oplm(self):
        return "{},{},{},{},{},{},{},{},{}".format(*self._device.oplm)

    @if_connected
    def get_lims(self):
        return "{},{},{},{},{},{},{},{},{}".format(*self._device.lims)
