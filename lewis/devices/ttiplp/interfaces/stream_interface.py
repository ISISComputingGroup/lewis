from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder


class TtiplpStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("ident").escape("*IDN?").eos().build(),
        CmdBuilder("get_volt_sp").escape("V").int().escape("?").eos().build(),
        CmdBuilder("set_volt_sp").escape("V").int().escape(" ").float().eos().build(),
        CmdBuilder("get_volt").escape("V").int().escape("O?").eos().build(),
        CmdBuilder("get_curr_sp").escape("I").int().escape("?").eos().build(),
        CmdBuilder("set_curr_sp").escape("I").int().escape(" ").float().eos().build(),
        CmdBuilder("get_curr").escape("I").int().escape("O?").eos().build(),
        CmdBuilder("get_output").escape("OP").int().escape("?").eos().build(),
        CmdBuilder("set_output").escape("OP").int().escape(" ").float().eos().build(),
        CmdBuilder("set_overvolt").escape("OVP").int().escape(" ").float().eos().build(),
        CmdBuilder("get_overvolt").escape("OVP").int().escape("?").eos().build(),
        CmdBuilder("set_overcurr").escape("OCP").int().escape(" ").float().eos().build(),
        CmdBuilder("get_overcurr").escape("OCP").int().escape("?").eos().build(),
        CmdBuilder("get_event_stat_reg").escape("LSR").int().escape("?").eos().build(),
        CmdBuilder("reset_trip").escape("TRIPRST").eos().build(),
    }

    in_terminator = "\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    def ident(self):
        return self.device.ident

    def get_volt(self, _):
        volt = self.device.get_volt()
        return "{:.4f}V".format(volt)

    def get_curr(self, _):
        curr = self.device.get_curr()
        return "{:.4f}A".format(curr)

    def set_volt_sp(self, _, volt_sp):
        self.device.set_volt_sp(float(volt_sp))

    def get_volt_sp(self, _):
        return "V1 {:.3f}".format(self.device.volt_sp)

    def set_curr_sp(self, _, curr_sp):
        self.device.set_curr_sp(float(curr_sp))

    def get_curr_sp(self, _):
        return "I1 {:.4f}".format(self.device.curr_sp)

    def set_output(self, _, output):
        self.device.set_output(output)

    def get_output(self, _):
        return "{:.0f}".format(self.device.output)

    def set_overvolt(self, _, overvolt):
        self.device.set_overvolt(float(overvolt))

    def get_overvolt(self, _):
        return "VP1 {:.3f}".format(self.device.overvolt)

    def set_overcurr(self, _, overcurr):
        self.device.set_overcurr(float(overcurr))

    def get_overcurr(self, _):
        return "CP1 {:.4f}".format(self.device.overcurr)

    def get_event_stat_reg(self, _):
        ret = 0
        if self.device.is_voltage_limited():  # Bit 0
            ret += 1
        if self.device.is_current_limited():  # Bit 1
            ret += 2
        if self.device.is_overvolt_tripped():  # Bit 2
            ret += 4
        if self.device.is_overcurrent_tripped():  # Bit 3
            ret += 8
        if self.device.is_hardware_tripped():  # Bit 6
            ret += 64
        return f"{ret}"

    def reset_trip(self):
        self.device.reset_trip()
