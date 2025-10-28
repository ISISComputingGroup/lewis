from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder


class Itc503StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("set_p").escape("P").float().eos().build(),
        CmdBuilder("set_i").escape("I").float().eos().build(),
        CmdBuilder("set_d").escape("D").float().eos().build(),
        CmdBuilder("get_p").escape("R8").eos().build(),
        CmdBuilder("get_i").escape("R9").eos().build(),
        CmdBuilder("get_d").escape("R10").eos().build(),
        CmdBuilder("get_gas_flow").escape("R7").eos().build(),
        CmdBuilder("set_gas_flow").escape("G").float().eos().build(),
        CmdBuilder("get_temp").escape("R1").eos().build(),
        CmdBuilder("get_temp").escape("R2").eos().build(),
        CmdBuilder("get_temp").escape("R3").eos().build(),
        CmdBuilder("get_temp_sp").escape("R0").eos().build(),
        CmdBuilder("set_temp").escape("T").float().eos().build(),
        CmdBuilder("get_status").escape("X").eos().build(),
        CmdBuilder("set_ctrl").escape("C").int().eos().build(),
        CmdBuilder("set_mode").escape("A").int().eos().build(),
        CmdBuilder("set_ctrl_chan").escape("H").int().eos().build(),
        CmdBuilder("set_autopid_on").escape("L1").eos().build(),
        CmdBuilder("set_autopid_off").escape("L0").eos().build(),
        CmdBuilder("set_heater_maxv").escape("M").float().eos().build(),
        # No readback for max heater output
        CmdBuilder("set_heater_v").escape("O").float().eos().build(),
        CmdBuilder("get_heater_v").escape("R6").eos().build(),
        CmdBuilder("get_heater_p").escape("R5").eos().build(),
        CmdBuilder("get_temp_error").escape("R4").eos().build(),
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

    def set_p(self, p):
        self.device.p = float(p)
        return "P"

    def get_p(self):
        return "R{:.1f}".format(self.device.p)

    def set_i(self, i):
        self.device.i = float(i)
        return "I"

    def get_i(self):
        return "R{:.1f}".format(self.device.i)

    def set_d(self, d):
        self.device.d = float(d)
        return "D"

    def get_d(self):
        return "R{:.1f}".format(self.device.d)

    def set_gas_flow(self, flow):
        self.device.gas_flow = float(flow)
        return "G"

    def get_gas_flow(self):
        return "R{:.1f}".format(self.device.gas_flow)

    def get_temp(self):
        return "R{:.1f}".format(self.device.temperature)

    def set_temp(self, temp):
        self.device.temperature_sp = float(temp)
        return "T"

    def get_temp_sp(self):
        return "R{:.1f}".format(self.device.temperature_sp)

    def get_status(self):
        if self.device.report_sweep_state_with_leading_zero:
            format_string = (
                "X0A{mode}C{ctrl}S{sweeping:02d}H{control_channel}L{autopid}"
            )
        else:
            format_string = (
                "X0A{mode}C{ctrl}S{sweeping:01d}H{control_channel}L{autopid}"
            )

        return format_string.format(
            mode=self.device.mode,
            ctrl=self.device.control,
            sweeping=1 if self.device.sweeping else 0,
            control_channel=self.device.control_channel,
            autopid=1 if self.device.autopid else 0,
        )

    def set_ctrl(self, ctrl):
        self.device.control = int(ctrl)
        return "C"

    def set_mode(self, mode):
        self.device.mode = int(mode)
        return "A"

    def set_ctrl_chan(self, chan):
        if not 1 <= int(chan) <= 3:
            raise ValueError("Invalid channel")
        self.device.control_channel = int(chan)
        return "H"

    def set_autopid_on(self):
        self.device.autopid = True
        return "L"

    def set_autopid_off(self):
        self.device.autopid = False
        return "L"

    def set_heater_v(self, manv):
        self.device.heater_v = float(manv)
        return "O"

    def get_heater_v(self):
        return "R{:.1f}".format(self.device.heater_v)

    def get_heater_p(self):
        # Return heater voltage number as a substitute for percentage.
        return "R{:.1f}".format(self.device.heater_v)

    def set_heater_maxv(self, volts):
        raise ValueError("At ISIS, do not use this command!")

    def get_temp_error(self):
        return "R{:.1f}".format(
            abs(self.device.temperature_sp - self.device.temperature)
        )
