from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder


@has_log
class Kynctm3KStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        Cmd("return_data", "MM,1111111111111111$"),
        CmdBuilder("change_input_mode").enum("Q0", "R0", "R1").build(),
        CmdBuilder("toggle_autosend").escape("SW,EA,").enum("1", "0").build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    def return_data(self):
        return_data = self._device.format_output_data()
        self.log.info("Returning {}".format(return_data))
        return return_data

    def change_input_mode(self, new_state):
        return self._device.set_input_mode(new_state)

    def toggle_autosend(self, new_state):
        return self._device.set_autosend_status(int(new_state))

    def handle_error(self, request, error):
        err = "An error occurred at request {}: {}".format(request, error)
        self.log.error(err)
        return str(err)
