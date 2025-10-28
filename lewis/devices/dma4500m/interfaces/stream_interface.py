from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


@has_log
class DMA4500MStreamInterface(StreamInterface):
    in_terminator = "\r"
    out_terminator = "\r"

    # Commands that we expect via serial during normal operation
    def __init__(self):
        super(DMA4500MStreamInterface, self).__init__()
        self.commands = {
            CmdBuilder(self.start).escape("start").eos().build(),
            CmdBuilder(self.abort).escape("abort").eos().build(),
            CmdBuilder(self.finished).escape("finished").eos().build(),
            CmdBuilder(self.set_temperature)
            .escape("set")
            .optional(" ")
            .escape("temperature ")
            .arg(".+")
            .eos()
            .build(),
            CmdBuilder(self.get_data)
            .escape("get")
            .optional(" ")
            .escape("data")
            .eos()
            .build(),
            CmdBuilder(self.get_raw_data)
            .escape("get")
            .optional(" ")
            .escape("raw")
            .optional(" ")
            .escape("data")
            .eos()
            .build(),
        }

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    @if_connected
    def start(self):
        return self._device.start()

    @if_connected
    def abort(self):
        return self._device.abort()

    @if_connected
    def finished(self):
        return self._device.finished()

    @if_connected
    def set_temperature(self, temperature_arg):
        try:
            temperature = float(temperature_arg)
        except ValueError:
            return "the given temperature could not be parsed"

        return self._device.set_temperature(temperature)

    @if_connected
    def get_data(self):
        return self._device.get_data()

    @if_connected
    def get_raw_data(self):
        return self._device.get_raw_data()
