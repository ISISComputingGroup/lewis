from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder

from ..device import Direction


class Wm323StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_status").escape("1RS").eos().build(),
        CmdBuilder("set_speed").escape("1SP ").float().eos().build(),
        CmdBuilder("set_rotation_cw").escape("1RR").eos().build(),
        CmdBuilder("set_rotation_ccw").escape("1RL").eos().build(),
        CmdBuilder("set_running_start").escape("1GO").eos().build(),
        CmdBuilder("set_running_stop").escape("1ST").eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    def get_status(self):
        running_int = 0
        if self.device.running:
            running_int = 1
        return "{} {} {} {} !".format(
            self.device.type, self.device.speed, self.device.direction.name, running_int
        )

    def set_speed(self, speed):
        self.device.speed = speed

    def set_rotation_cw(self):
        self.device.direction = Direction.CW

    def set_rotation_ccw(self):
        self.device.direction = Direction.CCW

    def set_running_start(self):
        self.device.running = True

    def set_running_stop(self):
        self.device.running = False
