from lewis.adapters.stream import Cmd, StreamInterface


class IrisCryoValveStreamInterface(StreamInterface):
    commands = {
        Cmd("get_status", "^\?$"),
        Cmd("set_open", "^OPEN$"),
        Cmd("set_closed", "^CLOSE$"),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    def get_status(self):
        status = "OPEN" if self._device.is_open else "CLOSED"
        return "SOLENOID " + status

    def set_open(self):
        self._device.is_open = True
        return ""

    def set_closed(self):
        self._device.is_open = False
        return ""

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
