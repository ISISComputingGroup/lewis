from enum import Enum

from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")
if_input_error = conditional_reply("input_correct", "ER,OF,00")


class Modes(Enum):
    """Device Modes
    """

    MEASURE = "R0"  # Read measured values
    SET_UP = "Q0"  # Configure device parameters


class KeylkgStreamInterface(StreamInterface):
    terminator = "\r"

    def __init__(self):
        super(KeylkgStreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.set_mode).arg("Q0|R0").eos().build(),
            CmdBuilder(self.set_measurement_offset)
            .escape("SW,OF,")
            .int()
            .escape(",")
            .float()
            .eos()
            .build(),
            CmdBuilder(self.get_measurement_offset).escape("SR,OF,").float().eos().build(),
            CmdBuilder(self.get_measurement_mode).escape("SR,HB,").int().eos().build(),
            CmdBuilder(self.set_measurement_mode)
            .escape("SW,HB,")
            .int()
            .escape(",")
            .int()
            .eos()
            .build(),
            CmdBuilder(self.get_measurement_value).escape("M").int().eos().build(),
            CmdBuilder(self.reset_measurement).escape("VR,").int().eos().build(),
        }

    @if_connected
    def reset_measurement(self, measurement_head):
        if self.device.mode == "Q0":
            return "ER,VR,01"
        else:
            if measurement_head == 0:
                self.device.detector_1_raw_value = 0.0000
                self.device.detector_2_raw_value = 0.0000
            elif measurement_head == 1:
                self.device.detector_1_raw_value = 0.0000
            elif measurement_head == 2:
                self.device.detector_2_raw_value = 0.0000
            return "VR"

    @if_connected
    def get_measurement_value(self, measurement_head):
        detector_1_value = self.device.detector_1_raw_value - self.device.detector_1_offset
        detector_2_value = self.device.detector_2_raw_value - self.device.detector_2_offset

        if measurement_head == 0:
            return (
                "ER,M0,01"
                if self.device.mode == Modes.SET_UP
                else "M0,{0:+08.4f},{1:+08.4f}".format(detector_1_value, detector_2_value)
            )
        elif measurement_head == 1:
            return (
                "ER,M1,01"
                if self.device.mode == Modes.SET_UP
                else "M1,{:+08.4f}".format(detector_1_value)
            )
        elif measurement_head == 2:
            return (
                "ER,M2,01"
                if self.device.mode == Modes.SET_UP
                else "M2,{:+08.4f}".format(detector_2_value)
            )

    @if_connected
    def set_measurement_mode(self, measurement_head, function):
        if self.device.mode == "R0":
            return "ER,HB,01"
        else:
            if measurement_head == 1:
                self.device.detector_1_measurement_mode = function
            elif measurement_head == 2:
                self.device.detector_2_measurement_mode = function
            return "SW,HB"

    @if_connected
    def get_measurement_mode(self, measurement_head):
        if self.device.mode == "R0":
            return "ER,HB,01"
        else:
            if measurement_head == 1:
                return "SR,HB,1,{0}".format(self.device.detector_1_measurement_mode)
            elif measurement_head == 2:
                return "SR,HB,2,{0}".format(self.device.detector_2_measurement_mode)

    @if_connected
    @if_input_error
    def set_measurement_offset(self, measurement_head, offset_value):
        # The device requires a +07d formatted input that is converted to within the
        # (-99.999, 99.000) limits. We convert this so that our read back will be correct.
        converted_value = offset_value * 10e-5

        if self.device.mode == "R0":
            return "ER,OF,01"
        else:
            if measurement_head == 0:
                self.device.detector_1_offset = converted_value
                self.device.detector_2_offset = converted_value
            elif measurement_head == 1:
                self.device.detector_1_offset = converted_value
            elif measurement_head == 2:
                self.device.detector_2_offset = converted_value
            return "SW,OF"

    @if_connected
    def get_measurement_offset(self, measurement_head):
        if self.device.mode == "R0":
            return "ER,OF,01"
        else:
            if measurement_head == 1:
                return "SR,OF,1,{:+08.4f}".format(self.device.detector_1_offset)
            elif measurement_head == 2:
                return "SR,OF,2,{:+08.4f}".format(self.device.detector_2_offset)

    @if_connected
    def set_mode(self, new_mode):
        if self.device.mode == new_mode:
            return "ER,{mode},01".format(mode=new_mode)
        else:
            self.device.mode = Modes(new_mode)
            return new_mode
