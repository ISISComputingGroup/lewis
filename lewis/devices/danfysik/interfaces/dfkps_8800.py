"""Stream device for danfysik 8800
"""

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from .dfkps_base import CommonStreamInterface

__all__ = ["Danfysik8800StreamInterface"]


@has_log
class Danfysik8800StreamInterface(CommonStreamInterface, StreamInterface):
    """Stream interface for a Danfysik model 8800.
    """

    protocol = "model8800"

    commands = CommonStreamInterface.commands + [
        CmdBuilder("set_current").escape("WA ").int().eos().build(),
        CmdBuilder("get_current").escape("ADCV").eos().build(),
        CmdBuilder("init_comms").escape("ADR 000").build(),
    ]

    @conditional_reply("connected")
    @conditional_reply("comms_initialized")
    def get_status(self):
        """Respond to the get_status command (S1)
        """
        response = (
            "{spare}{user1}{user2}{user3}{user4}{user5}{user6}{fw_diode_overtemp}{low_water_flow}{door_open}"
            "{pol_normal}{pol_reversed}{spare}{spare}{spare}{spare}{diode_heatsink}{chassis_overtemp}"
            "{igbt_heatsink_overtemp}{hf_diode_overtemp}{switch_reg_ddct_fail}{switch_reg_supply_fail}"
            "{igbt_driver_fail}{spare}{spare}{ac_undervolt}{spare}{ground_ripple}{ground_leak}"
            "{overcurrent}{power_on}{ready}".format(
                spare=self.bit(False),
                user1=self.interlock("user1"),
                user2=self.interlock("user2"),
                user3=self.interlock("user3"),
                user4=self.interlock("user4"),
                user5=self.interlock("user5"),
                user6=self.interlock("user6"),
                pol_normal=self.bit(not self.device.negative_polarity),
                pol_reversed=self.bit(self.device.negative_polarity),
                fw_diode_overtemp=self.interlock("fw_diode_overtemp"),
                low_water_flow=self.interlock("low_water_flow"),
                door_open=self.interlock("door_open"),
                diode_heatsink=self.interlock("diode_heatsink"),
                chassis_overtemp=self.interlock("chassis_overtemp"),
                igbt_heatsink_overtemp=self.interlock("igbt_heatsink_overtemp"),
                hf_diode_overtemp=self.interlock("hf_diode_overtemp"),
                switch_reg_ddct_fail=self.interlock("switch_reg_ddct_fail"),
                switch_reg_supply_fail=self.interlock("switch_reg_supply_fail"),
                igbt_driver_fail=self.interlock("igbt_driver_fail"),
                ac_undervolt=self.interlock("ac_undervolt"),
                ground_ripple=self.interlock("ground_ripple"),
                ground_leak=self.interlock("ground_leak"),
                overcurrent=self.interlock("overcurrent"),
                power_on=self.bit(not self.device.power),
                ready=self.bit(self.device.power),
            )
        )

        assert len(response) == 32
        return response
