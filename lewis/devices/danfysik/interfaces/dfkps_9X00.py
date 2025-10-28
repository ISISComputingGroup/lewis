"""Stream device for danfysik 9X00"""

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from .dfkps_base import CommonStreamInterface

__all__ = ["Danfysik9X00StreamInterface"]


@has_log
class Danfysik9X00StreamInterface(CommonStreamInterface, StreamInterface):
    """Stream interface for a Danfysik model 9100."""

    in_terminator = "\r"
    out_terminator = "\n\r"

    protocol = "model9X00"

    # This is the address of the LOQ danfysik 8500
    PSU_ADDRESS = 75

    commands = CommonStreamInterface.commands + [
        CmdBuilder("set_current").escape("DA 0 ").int().eos().build(),
        CmdBuilder("get_current").escape("AD 8").eos().build(),
        CmdBuilder("set_address").escape("ADR ").int().eos().build(),
        CmdBuilder("get_address").escape("ADR").eos().build(),
        CmdBuilder("init_comms").escape("REM").eos().build(),
        CmdBuilder("init_comms").escape("UNLOCK").eos().build(),
        CmdBuilder("get_slew_rate")
        .escape("R")
        .arg(r"[1-3]", argument_mapping=int)
        .eos()
        .build(),
        CmdBuilder("set_slew_rate")
        .escape("W")
        .arg(r"[1-3]", argument_mapping=int)
        .spaces()
        .int()
        .eos()
        .build(),
    ]

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_status(self):
        """Respond to the get_status command (S1)"""
        response = (
            "{power_off}{pol_normal}{pol_reversed}{spare}{crowbar}{imode}{is_percent}{external_interlock_0}"
            "{spare}{sum_interlock}{over_voltage}{dc_overcurrent}{dc_undervoltage}{spare}"
            "{phase_fail}{spare}{earth_leak_fail}{fan}{mps_overtemperature}"
            "{external_interlock_1}{external_interlock_2}{external_interlock_3}{mps_not_ready}{spare}".format(
                spare=self.bit(False),
                power_off=self.bit(not self.device.power),
                pol_normal=self.bit(not self.device.negative_polarity),
                pol_reversed=self.bit(self.device.negative_polarity),
                crowbar=self.bit(False),
                imode=self.bit(False),
                is_percent=self.bit(False),
                external_interlock_0=self.interlock("external_interlock_0"),
                sum_interlock=self.bit(len(self.device.active_interlocks) > 0),
                dc_overcurrent=self.interlock("dc_overcurrent"),
                over_voltage=self.interlock("over_voltage"),
                dc_undervoltage=self.interlock("dc_undervoltage"),
                phase_fail=self.interlock("phase_fail"),
                earth_leak_fail=self.interlock("earth_leak_fail"),
                fan=self.interlock("fan"),
                mps_overtemperature=self.interlock("mps_overtemperature"),
                external_interlock_1=self.interlock("external_interlock_1"),
                external_interlock_2=self.interlock("external_interlock_2"),
                external_interlock_3=self.interlock("external_interlock_3"),
                mps_not_ready=self.bit(not self.device.power),
            )
        )

        assert len(response) == 24, "length should have been 24 but was {}".format(
            len(response)
        )
        return response

    def set_address(self, value):
        self.device.set_address(value)

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_address(self):
        return "{:03d}".format(self.address)

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_slew_rate(self, dac_num):
        return self.device.get_slew_rate(dac_num)

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def set_slew_rate(self, dac_num, slew_rate_value):
        self.device.set_slew_rate(dac_num, slew_rate_value)
