from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


class RkndioStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_idn").escape("*IDN?").eos().build(),
        CmdBuilder("get_status").escape("STATUS").eos().build(),
        CmdBuilder("get_error").escape("ERR").eos().build(),
        CmdBuilder("get_d_i_state").escape("READ ").arg("2|3|4|5|6|7").eos().build(),
        CmdBuilder("set_d_o_state")
        .escape("WRITE ")
        .arg("8|9|10|11|12|13")
        .escape(" ")
        .arg("FALSE|TRUE")
        .eos()
        .build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        """Prints an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            None.
        """
        self.log.error(
            "An error occurred at request " + repr(request) + ": " + repr(error)
        )

        print("An error occurred at request {}: {}".format(request, error))

    @conditional_reply("connected")
    def get_idn(self):
        return self._device.idn

    @conditional_reply("connected")
    def get_status(self):
        return self._device.status

    @conditional_reply("connected")
    def get_error(self):
        return self._device.error

    @conditional_reply("connected")
    def get_d_i_state(self, pin):
        return self._device.get_input_state(pin)

    @conditional_reply("connected")
    def set_d_o_state(self, pin, state):
        return self._device.set_output_state(pin, state)
