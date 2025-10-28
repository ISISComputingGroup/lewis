from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


@has_log
class MezfliprStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("set_compensation")
        .escape("compensation_current=")
        .float()
        .eos()
        .build(),
        CmdBuilder("get_compensation").escape("compensation_current?").eos().build(),
        CmdBuilder("set_state").escape("device_state=").enum("off", "on").eos().build(),
        CmdBuilder("get_state").escape("device_state?").eos().build(),
        CmdBuilder("get_mode").escape("mode?").eos().build(),
        CmdBuilder("get_params").escape("flipper_params?").eos().build(),
        CmdBuilder("set_flipper_current")
        .escape("flipper_current=")
        .float()
        .eos()
        .build(),
        CmdBuilder("set_flipper_steps").escape("flipper_steps=").any().eos().build(),
        CmdBuilder("set_flipper_analytical")
        .escape("flipper_analytical=")
        .any()
        .eos()
        .build(),
        CmdBuilder("set_flipper_filename")
        .escape("flipper_filename=")
        .any()
        .eos()
        .build(),
    }

    in_terminator = "\n"
    out_terminator = "\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    @if_connected
    def set_compensation(self, compensation):
        self._device.compensation = compensation
        return "compensation_current={}".format(compensation)

    @if_connected
    def get_compensation(self):
        return "{}".format(self._device.compensation)

    @if_connected
    def get_state(self):
        return "on" if self._device.powered_on else "off"

    @if_connected
    def set_state(self, state):
        if state not in ["on", "off"]:
            raise ValueError("Invalid state")

        self._device.powered_on = state == "on"
        return "device_state={}".format(state)

    @if_connected
    def get_mode(self):
        return self._device.mode

    @if_connected
    def get_params(self):
        self.log.info("Params are: {}".format(self._device.params))
        return "{}".format(self._device.params)

    @if_connected
    def set_flipper_current(self, params):
        self._device.params = params
        self._device.mode = "static"
        return "flipper_current={}".format(params)

    @if_connected
    def set_flipper_steps(self, params):
        self._device.params = params
        self._device.mode = "steps"
        return "flipper_steps={}".format(params)

    @if_connected
    def set_flipper_analytical(self, params):
        self._device.params = params
        self._device.mode = "analytical"
        return "flipper_analytical={}".format(params)

    @if_connected
    def set_flipper_filename(self, params):
        self._device.params = params
        self._device.mode = "file"
        return "flipper_filename={}".format(params)
