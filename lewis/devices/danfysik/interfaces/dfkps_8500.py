"""Stream device for danfysik 8500"""

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from .dfkps_base import CommonStreamInterface

__all__ = ["Danfysik8500StreamInterface"]


@has_log
class Danfysik8500StreamInterface(CommonStreamInterface, StreamInterface):
    """Stream interface for a Danfysik model 8500."""

    in_terminator = "\r"
    out_terminator = "\n\r"

    protocol = "model8500"

    # This is the address of the LOQ danfysik 8500
    PSU_ADDRESS = 75

    commands = CommonStreamInterface.commands + [
        # See https://github.com/ISISComputingGroup/IBEX/issues/8502 for justification about why
        # we are using WA over DA 0
        CmdBuilder("set_current").escape("WA ").int().eos().build(),
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
    def get_status(self) -> str:
        """Respond to the get_status command (S1)"""
        response = (
            "{power_off}{pol_normal}{pol_reversed}{reg_transformer}{dac16}{dac17}{is_percent}{spare}"
            "{transistor_fault}{sum_interlock}{dc_overcurrent}{dc_overload}{reg_mod_fail}{prereg_fail}"
            "{phase_fail}{mps_waterflow_fail}{earth_leak_fail}{thermal_fail}{mps_overtemperature}"
            "{door_switch}{mag_waterflow_fail}{mag_overtemp}{mps_not_ready}{spare}".format(
                spare=self.bit(False),
                power_off=self.bit(not self.device.power),
                pol_normal=self.bit(not self.device.negative_polarity),
                pol_reversed=self.bit(self.device.negative_polarity),
                reg_transformer=self.bit(False),
                dac16=self.bit(False),
                dac17=self.bit(False),
                is_percent=self.bit(False),
                transistor_fault=self.interlock("transistor_fault"),
                sum_interlock=self.bit(len(self.device.active_interlocks) > 0),
                dc_overcurrent=self.interlock("dc_overcurrent"),
                dc_overload=self.interlock("dc_overload"),
                reg_mod_fail=self.interlock("reg_mod_fail"),
                prereg_fail=self.interlock("prereg_fail"),
                phase_fail=self.interlock("phase_fail"),
                mps_waterflow_fail=self.interlock("mps_waterflow_fail"),
                earth_leak_fail=self.interlock("earth_leak_fail"),
                thermal_fail=self.interlock("thermal_fail"),
                mps_overtemperature=self.interlock("mps_overtemperature"),
                door_switch=self.interlock("door_switch"),
                mag_waterflow_fail=self.interlock("mag_waterflow_fail"),
                mag_overtemp=self.interlock("mag_overtemp"),
                mps_not_ready=self.bit(not self.device.power),
            )
        )

        assert len(response) == 24, "length should have been 24 but was {}".format(
            len(response)
        )

        return response

    def set_address(self, value: int) -> None:
        self.device.set_address(value)

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_address(self) -> str:
        return "{:03d}".format(self.address)

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_slew_rate(self, dac_num: int) -> float:
        return self.device.get_slew_rate(dac_num)

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def set_slew_rate(self, dac_num: int, slew_rate_value: float) -> None:
        self.device.set_slew_rate(dac_num, slew_rate_value)
