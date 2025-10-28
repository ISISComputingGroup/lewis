"""Stream device for danfysik 8000"""

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from .dfkps_base import CommonStreamInterface

__all__ = ["Danfysik8000StreamInterface"]


@has_log
class Danfysik8000StreamInterface(CommonStreamInterface, StreamInterface):
    """Stream interface for a Danfysik model 8000."""

    protocol = "model8000"

    commands = CommonStreamInterface.commands + [
        CmdBuilder("set_current").escape("DA 0 ").int().eos().build(),
        CmdBuilder("get_current").escape("AD 8").eos().build(),
        CmdBuilder("init_comms").escape("UNLOCK").build(),
    ]

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_status(self):
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

        assert len(response) == 24, "length should have been 24 but was {}".format(len(response))
        return response
