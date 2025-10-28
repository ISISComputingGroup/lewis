from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply, timed_reply

if_connected = conditional_reply("connected")
if_input_error = conditional_reply("input_correct", "%%[Error:stack underflow]%%")
if_valid_input_delay = timed_reply(action="crash_pump", minimum_time_delay=100)


def combined_checks(func):
    """Combine all conditional reply checks so we have a single decorator"""
    return if_valid_input_delay(if_connected(if_input_error(func)))


class Jsco4180StreamInterface(StreamInterface):
    in_terminator = "\r"
    out_terminator = "\r\n"

    def __init__(self):
        super(Jsco4180StreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.set_flowrate).float().escape(" flowrate set").eos().build(),
            CmdBuilder(self.get_flowrate_rbv).escape("flowrate load p").eos().build(),
            CmdBuilder(self.get_flowrate).escape("a_flow load p").eos().build(),
            CmdBuilder(self.get_pressure).escape("a_press1 load p").eos().build(),
            CmdBuilder(self.set_pressure_max).int().escape(" pmax set").build(),
            CmdBuilder(self.get_pressure_max).escape("a_pmax load p").eos().build(),
            CmdBuilder(self.set_pressure_min).int().escape(" pmin set").build(),
            CmdBuilder(self.get_pressure_min).escape("a_pmin load p").eos().build(),
            CmdBuilder(self.get_program_runtime).escape("current_time load p").eos().build(),
            CmdBuilder(self.get_component_a).escape("compa load p").eos().build(),
            CmdBuilder(self.get_component_b).escape("compb load p").eos().build(),
            CmdBuilder(self.get_component_c).escape("compc load p").eos().build(),
            CmdBuilder(self.get_component_d).escape("compd load p").eos().build(),
            CmdBuilder(self.set_composition)
            .float()
            .escape(" ")
            .float()
            .escape(" ")
            .float()
            .escape(" ")
            .float()
            .escape(" comp set")
            .eos()
            .build(),
            CmdBuilder(self.get_error).escape("trouble load p").eos().build(),
            CmdBuilder(self.set_error).escape("0 trouble set").build(),
            CmdBuilder(self.set_pump).int().escape(" pump set").eos().build(),
            CmdBuilder(self.get_status).escape("status load p").eos().build(),
            CmdBuilder(self.set_file_number).int().escape(" fileno set").eos().build(),
            CmdBuilder(self.set_file_open).int().escape(" openfile").eos().build(),
            CmdBuilder(self.set_file_closed).int().escape(" closefile").eos().build(),
        }

    def catch_all(self):
        pass

    @combined_checks
    def set_file_open(self, _):
        self.device.file_open = True

    @combined_checks
    def set_file_closed(self, _):
        self.device.file_open = False

    @combined_checks
    def set_file_number(self, file_number):
        state = self.device.state
        if state != "pump_off":
            return "%%[Program is Busy]%%" + self.out_terminator
        else:
            self.device.file_number = file_number
            self.device.single_channel_mode = False

    @combined_checks
    def get_status(self):
        if self.device.status == "pump_off":
            return 0
        elif self.device.status == "pump_on":
            return 33  # Running program but time halted
        elif self.device.status == "pump_program":
            return 49  # Running program with time
        elif self.device.status == "pump_program_reset":
            return 49  # Running program with reset timer

    @combined_checks
    def set_pump(self, mode):
        if mode == 0:
            # Pump on
            self.device.status = "pump_on"
        elif mode == 1:
            # Pump off
            self.device.status = "pump_off"
            return self.out_terminator
        elif mode == 6:
            # Pump program (time increment halted)
            self.device.status = "pump_program"
            return self.out_terminator
        elif mode == 8:
            # Pump reset and rerun program
            self.device.status = "pump_program_reset"
            self.device.program_runtime = 0
            return self.out_terminator

    @combined_checks
    def set_flowrate(self, flowrate):
        self.device.flowrate_rbv = flowrate
        return self.out_terminator

    @combined_checks
    def get_flowrate(self):
        return self.device.flowrate

    @combined_checks
    def get_flowrate_rbv(self):
        return self.device.flowrate_rbv

    @combined_checks
    def get_current_flowrate(self):
        return self.device.flowrate

    @combined_checks
    def get_pressure(self):
        return int(self.device.pressure)

    @combined_checks
    def set_pressure_max(self, pressure_max):
        self.device.pressure_max = pressure_max
        return self.out_terminator

    @combined_checks
    def get_pressure_max(self):
        return self.device.pressure_max

    @combined_checks
    def set_pressure_min(self, pressure_min):
        self.device.pressure_min = pressure_min
        return self.out_terminator

    @combined_checks
    def get_pressure_min(self):
        return self.device.pressure_min

    @combined_checks
    def get_program_runtime(self):
        if self.device.status == "pump_program_reset":
            self.device.program_runtime += 1
        return int(self.device.program_runtime)

    @combined_checks
    def get_component_a(self):
        return 100 if self.device.single_channel_mode else self.device.component_A

    @combined_checks
    def get_component_b(self):
        return 0 if self.device.single_channel_mode else self.device.component_B

    @combined_checks
    def get_component_c(self):
        return 0 if self.device.single_channel_mode else self.device.component_C

    @combined_checks
    def get_component_d(self):
        return 0 if self.device.single_channel_mode else self.device.component_D

    @combined_checks
    def set_composition(self, ramptime, a, b, c):
        self.device.component_A = a
        self.device.component_B = b
        self.device.component_C = c
        self.device.component_D = 100 - (a + b + c)
        return self.out_terminator

    @combined_checks
    def get_error(self):
        return self.device.error

    @combined_checks
    def set_error(self):
        self.device.error = 0
        return self.out_terminator
