"""Stream device for amint2l"""

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


@has_log
class Amint2lStreamInterface(StreamInterface):
    """Stream interface for the serial port"""

    in_terminator = chr(3)
    out_terminator = chr(3)

    def __init__(self):
        super(Amint2lStreamInterface, self).__init__()
        self.commands = {
            CmdBuilder(self.get_pressure).stx().arg("[A-Fa-f0-9]+").escape("r").build()
        }

    @if_connected
    def handle_error(self, request, error):
        """If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    @if_connected
    def get_pressure(self, address):
        """Gets the current pressure

        :param address: address of request
        Returns: pressure in correct format if pressure has a value; if None returns None as if it is disconnected

        """
        if address.upper() != self._device.address.upper():
            self.log.error("unknown address {0}".format(address))
            return None
        self.log.info("Pressure: {0}".format(self._device.pressure))
        if self._device.pressure is None:
            return None
        else:
            try:
                return "{stx}{pressure:+8.3f}".format(stx=chr(2), pressure=self._device.pressure)
            except ValueError:
                # pressure contains string probably OR (over range) or UR (under range)
                return "{stx}{pressure:8s}".format(stx=chr(2), pressure=self._device.pressure)
