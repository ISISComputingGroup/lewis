from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


@has_log
class MclennanStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("stop").int().escape("ST").eos().build(),
        CmdBuilder("identify").int().escape("ID").eos().build(),
        CmdBuilder("status").int().escape("OS").eos().build(),
        CmdBuilder("get_actual_position").int().escape("OA").eos().build(),
        CmdBuilder("get_command_position").int().escape("OC").eos().build(),
        CmdBuilder("set_accel").int().escape("SA").int().eos().build(),
        CmdBuilder("set_decel").int().escape("SD").int().eos().build(),
        CmdBuilder("set_creep_speed").int().escape("SC").int().eos().build(),
        CmdBuilder("reset").int().escape("RS").eos().build(),
        CmdBuilder("jog").int().escape("CV").int().eos().build(),
        CmdBuilder("query_speeds").int().escape("QS").eos().build(),
        CmdBuilder("set_mode").int().escape("CM").int().eos().build(),
        CmdBuilder("set_encoder_ratio").int().escape("ER").int().escape("/").int().eos().build(),
        CmdBuilder("set_window").int().escape("WI").int().eos().build(),
        CmdBuilder("set_timeout").int().escape("TO").int().eos().build(),
        CmdBuilder("set_tracking_window").int().escape("TR").int().eos().build(),
        CmdBuilder("enable_soft_limits").int().escape("SL").int().eos().build(),
        CmdBuilder("set_backoff").int().escape("BO").int().eos().build(),
        CmdBuilder("set_creep_steps").int().escape("CR").int().eos().build(),
        CmdBuilder("set_settle_time").int().escape("SE").int().eos().build(),
        CmdBuilder("set_abort_mode").int().escape("AM").arg("[0-1]{8}").eos().build(),
        CmdBuilder("set_datum_mode").int().escape("DM").arg("[0-1]{8}").eos().build(),
        CmdBuilder("set_home_pos").int().escape("SH").int().eos().build(),
        CmdBuilder("move_relative").int().escape("MR").int().eos().build(),
        CmdBuilder("move_absolute").int().escape("MA").int().eos().build(),
        CmdBuilder("set_velocity").int().escape("SV").int().eos().build(),
        CmdBuilder("home").int().escape("HD").int().eos().build(),
        CmdBuilder("set_ba").int().escape("BA").eos().build(),
        CmdBuilder("clear_datum").int().escape("CD").eos().build(),
        CmdBuilder("define_command_position").int().escape("CP").int().eos().build(),
        CmdBuilder("define_actual_position").int().escape("AP").int().eos().build(),
        CmdBuilder("query_mode").int().escape("QM").eos().build(),
        CmdBuilder("query_current_op").int().escape("CO").eos().build(),
        CmdBuilder("query_all").int().escape("QA").eos().build(),
        CmdBuilder("query_position").int().escape("QP").eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    @if_connected
    def stop(self, controller):
        self.device.stop()
        return "OK"

    @if_connected
    def identify(self, controller):
        return (
            f"{controller:02}: PM600 Ver 3.02"
            if not self.device.is_pm304
            else "1:Mclennan Servo Supplies Ltd. PM304 V6.15"
        )

    @if_connected
    def query_speeds(self, controller):
        return (
            f"SV={self.device.velocity[controller]},SC={self.device.creep_speed[controller]},SA={self.device.accl[controller]},SD={self.device.decl[controller]}"
            if self.device.is_pm304
            else f"{controller:02}:SC = {self.device.creep_speed[controller]} SV = {self.device.velocity[controller]} SA = {self.device.accl[controller]} SD = {self.device.decl[controller]} LD = 200000"
        )

    @if_connected
    def set_creep_speed(self, controller, creep_speed):
        self.device.creep_speed[controller] = creep_speed
        if controller == 1:
            self.device.creep_speed1 = creep_speed
        if controller == 2:
            self.device.creep_speed2 = creep_speed
        if controller == 3:
            self.device.creep_speed3 = creep_speed
        return "OK"

    @if_connected
    def status(self, controller):
        return f"{controller:02}:{int(self.device.is_idle)}000{int(self.device.is_jogging)}000"

    @if_connected
    def get_actual_position(self, controller):
        return f"{controller:02}:{int(self.device.position)}"

    def get_command_position(self, controller):
        return f"{controller:02}:{int(self.device.position)}"

    @if_connected
    def set_accel(self, controller, acceleration):
        self.device.accl[controller] = acceleration
        return "OK"

    @if_connected
    def set_decel(self, controller, deceleration):
        self.device.decl[controller] = deceleration
        return "OK"

    @if_connected
    def reset(self, controller):
        return "!RESET"

    @if_connected
    def jog(self, controller, velocity):
        self.device.jog(velocity)
        return "OK"

    @if_connected
    def set_mode(self, controller, mode):
        self.device.mode[controller] = mode
        return "OK"

    @if_connected
    def set_encoder_ratio(self, controller, er_num, er_denom):
        self.device.encoder_ratio[controller] = float(er_num) / float(er_denom)
        return "OK"

    @if_connected
    def set_window(self, controller, window):
        self.device.window[controller] = window
        return "OK"

    @if_connected
    def set_timeout(self, controller, timeout):
        self.device.timeout[controller] = timeout
        return "OK"

    @if_connected
    def set_tracking_window(self, controller, window):
        self.device.tracking_window[controller] = window
        return "OK"

    @if_connected
    def enable_soft_limits(self, controller, enable):
        self.device.enable_limits[controller] = enable
        return "OK"

    @if_connected
    def set_backoff(self, controller, value):
        self.device.backoff[controller] = value
        return "OK"

    @if_connected
    def set_creep_steps(self, controller, value):
        self.device.creep_steps[controller] = value
        return "OK"

    @if_connected
    def set_settle_time(self, controller, value):
        self.device.settle_time[controller] = value
        return "OK"

    @if_connected
    def set_abort_mode(self, controller, value):
        self.device.abort_mode[controller] = value
        return "OK"

    @if_connected
    def set_datum_mode(self, controller, value):
        self.device.datum_mode[controller] = value
        return "OK"

    @if_connected
    def set_home_pos(self, controller, value):
        self.device.home_pos[controller] = value
        return "OK"

    @if_connected
    def move_relative(self, controller, pos):
        self.device.moveRel(controller, pos)
        return "OK"

    @if_connected
    def move_absolute(self, controller, pos):
        self.device.moveAbs(controller, pos)
        return "OK"

    @if_connected
    def set_velocity(self, controller, value):
        self.device.velocity[controller] = value
        return "OK"

    @if_connected
    def home(self, controller, dir):
        self.device.home()
        return "OK"

    @if_connected
    def set_ba(self, controller):
        self.device.has_sent_BA = True
        return "OK"

    @if_connected
    def clear_datum(self, controller):
        return "OK"

    @if_connected
    def define_command_position(self, controller, value):
        self.device.target_position = value
        return "OK"

    @if_connected
    def define_actual_position(self, controller, value):
        self.device.position = value
        return "OK"

    @if_connected
    def query_mode(self, controller):
        return f"{controller:02}:CM = {self.device.mode[controller]} AM = {self.device.abort_mode[controller]} DM = {self.device.datum_mode[controller]} JM = 11000000"

    @if_connected
    def query_current_op(self, controller):
        return f"{controller:02}:{self.device.current_op}"

    # all replies should contain the original command string first and \r, the emulator does not do this in general but it
    # only matters for multiline replies which this is the only such command
    @if_connected
    def query_all(self, controller):
        lines = [
            "Mclennan Digiloop Motor Controller V2.10a(1.2)",
            f"Address = {controller}",
            "Privilege level = 4",
            "Mode = Aborted",
            "Kf = 1000 Kp = 500 Ks = 2000 Kv = 1000 Kx = 0",
            "Slew speed = 100000",
            "Acceleration = 200000 Deceleration = 400000",
            "Creep speed = 400 Creep steps = 0",
            "Jog speed = 100 Joystick speed = 10000",
            "Settling time = 200",
            "Window = 4 Threshold = 2000",
            "Tracking = 4000",
            "Lower soft limit = -2147483647 Upper soft limit = 2147483647",
            "Soft limits enabled",
            "Lower hard limit on Upper hard limit on",
            "Jog enabled Joystick disabled",
            "Gbox num = 1 Gbox den = 1",
            "Command pos = 0 Motor pos = 1",
            "Pos error = -1 Input pos = 0",
            "Valid sequences: none Autoexec disabled",
            "Valid cams: none",
            "Valid profiles: none Profile time = 1000 ms",
            "Read port: %00000000 Last write: %00000000",
        ]
        return f"{controller:02}QA\r" + "\r\n".join(lines)

    @if_connected
    def query_position(self, controller):
        return f"{controller:02}:CP = {self.device.target_position} AP = {self.device.position} IP = 1050 TP = 0 OD = -2050"
