from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


@has_log
class Dh2000StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_status").escape("&STS!").eos().build(),
        CmdBuilder("close_shutter").escape("&CLOSEA!").eos().build(),
        CmdBuilder("open_shutter").escape("&OPENA!").eos().build(),
        CmdBuilder("invalid_command").eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    ACK = "&ACK!" + out_terminator

    @staticmethod
    def handle_error(request, error):
        """Prints an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            None.
        """
        print("An error occurred at request {}: {}".format(request, error))

    @conditional_reply("is_connected")
    def invalid_command(self):
        return "&NAC!{}&TYPERR!".format(self.out_terminator)

    @conditional_reply("is_connected")
    def close_shutter(self):
        self._device.shutter_is_open = False

        return self.ACK

    @conditional_reply("is_connected")
    def open_shutter(self):
        self._device.shutter_is_open = True

        return self.ACK

    @conditional_reply("is_connected")
    def get_status(self):
        shutter = self._device.shutter_is_open
        interlock = self._device.interlock_is_triggered

        status_string = "{ACK}\n&A{shutter},B0,I{intlock}!".format(
            ACK=self.ACK, shutter=int(shutter), intlock=int(interlock)
        )

        return status_string
