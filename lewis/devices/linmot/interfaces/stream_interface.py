from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder


class LinmotStreamInterface(StreamInterface):
    in_terminator = "\r\n"
    out_terminator = "\r"

    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("set_position").escape("!SP").int().escape("A").eos().build(),
        CmdBuilder("get_position").escape("!GPA").eos().build(),
        CmdBuilder("get_actual_speed_resolution").escape("!VIA").eos().build(),
        CmdBuilder("get_motor_warn_status").escape("!EWA").eos().build(),
        CmdBuilder("get_motor_error_status").escape("!EEA").eos().build(),
        CmdBuilder("set_maximal_speed").escape("!SV").int().escape("A").eos().build(),
        CmdBuilder("set_maximal_acceleration").escape("!SA").int().escape("A").eos().build(),
    }

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    def set_position(self, target_position):
        self.device.move_to_target(target_position)
        return "#"

    def get_position(self):
        return "#{position}".format(position=self.device.position)

    def get_actual_speed_resolution(self):
        return "#{speed_resolution}".format(speed_resolution=self.device.speed_resolution)

    def get_motor_warn_status(self):
        return "#{motor_warn_status}".format(motor_warn_status=self.device.motor_warn_status.value)

    def get_motor_error_status(self):
        return "#{motor_error_status}".format(
            motor_error_status=self.device.motor_error_status.value
        )

    def set_maximal_speed(self, speed):
        self.device.velocity = int(speed)
        return "#"

    def set_maximal_acceleration(self, acceleration):
        self.device.maximal_acceleration = int(acceleration)
        return "#"
