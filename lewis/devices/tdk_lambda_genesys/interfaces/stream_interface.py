from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


class TDKLambdaGenesysStreamInterface(StreamInterface):
    commands = {
        CmdBuilder("write_voltage").escape("PV ").float().build(),
        CmdBuilder("read_setpoint_voltage").escape("PV?").build(),
        CmdBuilder("read_voltage").escape("MV?").build(),
        CmdBuilder("write_current").escape("PC ").float().build(),
        CmdBuilder("read_setpoint_current").escape("PC?").build(),
        CmdBuilder("read_current").escape("MC?").build(),
        CmdBuilder("remote").escape("RMT 1").build(),
        CmdBuilder("write_power").escape("OUT ").arg("[OFF|ON]").build(),
        CmdBuilder("read_power").escape("OUT?").build(),
        CmdBuilder("initialize_comms").escape("ADR ").int().eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    def handle_error(self, request, error):
        self.log.error(
            "Beep boop. Error occurred at " + repr(request) + ": " + repr(error)
        )
        print("Beep boop. Error occurred at " + repr(request) + ": " + repr(error))

    @conditional_reply("comms_initialized")
    def read_voltage(self):
        return self._device.voltage

    @conditional_reply("comms_initialized")
    def read_setpoint_voltage(self):
        return self._device.setpoint_voltage

    @conditional_reply("comms_initialized")
    def write_voltage(self, v):
        self._device.setpoint_voltage = v
        return "VOLTAGE SET TO: {}".format(v)

    @conditional_reply("comms_initialized")
    def read_current(self):
        return self._device.current

    @conditional_reply("comms_initialized")
    def read_setpoint_current(self):
        return self._device.setpoint_current

    @conditional_reply("comms_initialized")
    def write_current(self, c):
        self._device.setpoint_current = c
        return "VOLTAGE SET TO: {}".format(c)

    @conditional_reply("comms_initialized")
    def read_power(self):
        return self._device.powerstate

    @conditional_reply("comms_initialized")
    def write_power(self, p):
        self._device.powerstate = p
        return "POWER SET TO {}".format(p)

    @conditional_reply("comms_initialized")
    def remote(self):
        # We can ignore this command
        pass

    # This is the only command the device recognises when uninitialized
    def initialize_comms(self, addr):
        self.device.comms_initialized = True
