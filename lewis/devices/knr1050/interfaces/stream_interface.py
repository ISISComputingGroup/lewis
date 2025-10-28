from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")
if_input_error = conditional_reply("input_correct", "ERROR:20,Instrument in standalone mode")


@has_log
class Knr1050StreamInterface(StreamInterface):
    in_terminator = "\r"
    out_terminator = "\r"

    def __init__(self):
        super(Knr1050StreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.get_status).escape("STATUS?").eos().build(),
            CmdBuilder(self.start_pump)
            .escape("RAMP:0,")
            .int()
            .escape(",")
            .int()
            .escape(",")
            .int()
            .escape(",")
            .int()
            .escape(",")
            .int()
            .eos()
            .build(),
            CmdBuilder(self.stop_pump).escape("STOP:1,0").eos().build(),
            CmdBuilder(self.stop_klv).escape("STOP:2").eos().build(),
            CmdBuilder(self.get_pressure_limits).escape("PLIM?").eos().build(),
            CmdBuilder(self.set_pressure_limits)
            .escape("PLIM:")
            .int()
            .escape(",")
            .int()
            .eos()
            .build(),
            CmdBuilder(self.get_remote_mode).escape("REMOTE?").eos().build(),
            CmdBuilder(self.set_remote_mode).escape("REMOTE").eos().build(),
            CmdBuilder(self.set_local_mode).escape("LOCAL").eos().build(),
        }

    def handle_error(self, request, error):
        """If command is not recognised print and error
        Args:
            request: requested string
            error: problem
        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    @if_connected
    def start_pump(self, flow_rate, a, b, c, d):
        """Executes ramp starting from current execution time.

        Args:
            flow_rate (float): the flow rate in ul/min
            a (int): concentration A
            b (int): concentration B
            c (int): concentration C
            d (int): concentration D
        """
        self.device.flow_rate = flow_rate
        self.device.current_flow_rate = flow_rate
        # crude pressure simulation
        self.device.pressure = (
            int(self.device.pressure_limit_high) - int(self.device.pressure_limit_low) // 2
        )
        self.device.concentrations = [int(a), int(b), int(c), int(d)]

        self.device.pump_on = True

        self.stop_klv()
        return "OK"

    @if_connected
    def stop_pump(self):
        """Stop mode: Stop time table and data acquisition."""
        self.device.pump_on = False
        self.device.keep_last_values = False

        self.device.current_flow_rate = 0.0
        self.device.pressure = 0
        return "OK"

    @if_connected
    def stop_klv(self):
        """Stop mode: Keep last values."""
        self.device.keep_last_values = True
        return "OK"

    @if_connected
    @if_input_error
    def get_pressure_limits(self):
        return "PLIM:{},{}".format(self.device.pressure_limit_low, self.device.pressure_limit_high)

    @if_connected
    def set_pressure_limits(self, low, high):
        """Set the pressure limits on the device
        Args:
            low (int): The lower bound
            high (int): The upper bound

        Returns:
            'OK' (str) : Device confirmation
        """
        self.device.pressure_limit_low = int(low)
        self.device.pressure_limit_high = int(high)
        return "OK"

    @if_connected
    def get_status(self):
        return_params = [
            self.device.time_stamp,
            self.device.state_num,
            1 if self.device.curr_program_run_time else "",
            self.device.current_flow_rate,
        ]
        return_params.extend(self.device.concentrations)
        return_params.append(self.device.pressure)
        return "STATUS:{},{},0,{},{},{},{},{},{},0,0,0,0,0,0,0,0,{},0,0".format(*return_params)

    @if_connected
    def get_remote_mode(self):
        return "REMOTE:{}".format(1 if self.device.remote else 0)

    @if_connected
    def set_remote_mode(self):
        self.device.remote = True
        return "OK"

    @if_connected
    def set_local_mode(self):
        self.device.remote = False
        return "OK"
