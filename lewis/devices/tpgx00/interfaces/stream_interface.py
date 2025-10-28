from enum import Enum

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.constants import ACK
from lewis.utils.replies import conditional_reply

from ..device import CircuitAssignment


@has_log
class Tpgx00StreamInterfaceBase(object):
    """Stream interface for the serial port for either a TPG300 or TPG500."""

    ack_terminator = "\r\n"  # Acknowledged commands are terminated by this

    commands = {
        CmdBuilder("acknowledge_pressure")
        .escape("P")
        .arg("A1|A2|B1|B2")
        .escape(ack_terminator)
        .eos()
        .build(),
        CmdBuilder("acknowledge_units").escape("UNI").escape(ack_terminator).eos().build(),
        CmdBuilder("acknowledge_set_units")
        .escape("UNI")
        .escape(",")
        .arg("0|1|2|3|4|5|6")
        .escape(ack_terminator)
        .eos()
        .build(),
        CmdBuilder("acknowledge_function")
        .escape("SP")
        .arg("1|2|3|4|A|B")
        .escape(ack_terminator)
        .eos()
        .build(),
        CmdBuilder("acknowledge_set_function")
        .escape("SP")
        .arg("1|2|3|4|A|B")
        .escape(",")
        .arg(r"[+-]?\d+.\d+", float)
        .escape("E")
        .arg(r"(?:-|\+)(?:[1-9]+\d*|0)", int)
        .escape(",")
        .arg(r"[+-]?\d+.\d+", float)
        .escape("E")
        .arg(r"(?:-|\+)(?:[1-9]+\d*|0)", int)
        .escape(",")
        .int()
        .escape(ack_terminator)
        .eos()
        .build(),
        CmdBuilder("acknowledge_function_status")
        .escape("SPS")
        .escape(ack_terminator)
        .eos()
        .build(),
        CmdBuilder("acknowledge_error").escape("ERR").escape(ack_terminator).eos().build(),
        CmdBuilder("handle_enquiry")
        .enq()
        .build(),  # IMPORTANT: <ENQ> is not terminated with usual terminator
    }

    # Override StreamInterface attributes:
    in_terminator = ""  # Override the default terminator
    out_terminator = "\r\n"
    readtimeout = 1

    def handle_error(self, request, error):
        """Prints an error message if a command is not recognised, and sets the device
        error status accordingly.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            None.
        """
        self._device.error_status = "SYNTAX_ERROR"
        print("An error occurred at request {}: {}".format(request, error))

    @conditional_reply("connected")
    def acknowledge_pressure(self, channel):
        """Acknowledges a request to get the pressure and stores the request.

        Args:
            channel: (string) Pressure channel to read from.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = channel
        return ACK

    @conditional_reply("connected")
    def acknowledge_units(self):
        """Acknowledge that the request for current units was received.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = "UNI"
        return ACK

    @conditional_reply("connected")
    def acknowledge_set_units(self, units):
        """Acknowledge that the request to set the units was received.

        Args:
            units (integer): Takes the value 1, 2 or 3.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = "UNI" + str(units)
        return ACK

    @conditional_reply("connected")
    def acknowledge_function(self, function):
        """Acknowledge that the request for function thresholds was received.

        Args:
            function (string): Takes the value 1, 2, 3, 4, A or B. This it the switching
            function's settings that we want to read.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = "F" + function
        return ACK

    @conditional_reply("connected")
    def acknowledge_set_function(self, function, low_thr, low_exp, high_thr, high_exp, assign):
        """Acknowledge that the request to set the function thresholds was received.

        Args:
            function (string): Takes the value 1, 2, 3, 4, A or B. This is the switching
            function's settings that we want to set.

            low_thr (float): Lower threshold of the switching function.

            low_exp (int): Exponent of the lower threshold.

            high_thr (float): Upper threshold of the switching function.

            high_exp (int): Exponent of the upper threshold.

            assign (int): Circuit to be assigned to this switching function.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = "FS" + function
        self._device.switching_function_to_set = CircuitAssignment(
            low_thr, low_exp, high_thr, high_exp, self.get_sf_assignment_name(assign)
        )
        return ACK

    @conditional_reply("connected")
    def acknowledge_function_status(self):
        """Acknowledge that the request to check switching functions status was received

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = "SPS"
        return ACK

    @conditional_reply("connected")
    def acknowledge_error(self):
        """Acknowledge that the request to check the device error status was received.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device.readstate = "ERR"
        return ACK

    def handle_enquiry(self):
        """Handles an enquiry using the last command sent.

        Returns:
            String: Channel pressure and status if last command was in channels.
            String: Returns the devices current units if last command is 'UNI'.
            None: Sets the devices units to 1,2, or 3 if last command is 'UNI{}' where {} is 1, 2 or 3
                respectively.
            None: Last command unknown.
        """
        self.log.info(self._device.readstate)

        channels = ("A1", "A2", "B1", "B2")
        switching_functions_read = ("F1", "F2", "F3", "F4", "FA", "FB")
        switching_functions_set = ("FS1", "FS2", "FS3", "FS4", "FSA", "FSB")
        units_flags = ("UNI0", "UNI1", "UNI2", "UNI3", "UNI4", "UNI5", "UNI6")

        if self._device.readstate.name in channels:
            return self.get_pressure(self._device.readstate)

        elif self._device.readstate.name == "UNI":
            return self.get_units()

        elif self._device.readstate.name in units_flags:
            unit_num = int(self._device.readstate.name[-1])
            self.set_units(self.get_units_enum(unit_num))
            return self.get_units()

        elif self._device.readstate.name in switching_functions_read:
            return self.get_thresholds_readstate(self._device.readstate)

        elif self._device.readstate.name in switching_functions_set:
            self.set_threshold(self._device.readstate)
            readstate = self.get_readstate_val(self._device.readstate).replace("S", "", 1)
            return self.get_thresholds_readstate(self.get_readstate_enum(readstate))

        elif self._device.readstate.name == "SPS":
            status = self.get_switching_functions_status()
            return ",".join(status)

        elif self._device.readstate.name == "ERR":
            return self.get_error_status()

        else:
            self.log.info(
                "Last command was unknown. Current readstate is {}.".format(self._device.readstate)
            )

    def get_units(self):
        """Gets the units of the device.

        Returns:
            Name of the units.
        """
        return self.get_units_val(self._device.units)

    def set_units(self, units):
        """Sets the units on the device.

        Args:
            units (Units member): Units to be set

        Returns:
            None.
        """
        self._device.units = units

    def get_threshold(self, function):
        """Gets the settings of a switching function.

        Args:
            function: (string) the switching function to be set
        Returns:
            tuple containing a sequence of: high_threshold (float), high_exponent(int),
            low_threshold (float), low_exponent (int), circuit_assignment (SFAssignment enum member)
        """
        switching_function = function[-1]
        return self._device.switching_functions[switching_function]

    def set_threshold(self, function):
        """Sets the settings of a switching function.

        Args:
            function: (ReadState member) the switching function to be set

        Returns:
            None.
        """
        switching_function = self.get_readstate_val(function)[-1]
        self._device.switching_functions[switching_function] = (
            self._device.switching_function_to_set
        )

    def get_thresholds_readstate(self, readstate):
        """Helper method for getting thresholds of a function all in one string based on current readstate.

        Args:
            readstate: (ReadState member) the current read state
        Returns:
            a string containing the lower and higher threshold and the switching f-n assignment
        """
        function = self.get_threshold(self.get_readstate_val(readstate))
        return (
            str(function.high_threshold)
            + "E"
            + str(function.high_exponent)
            + ","
            + str(function.low_threshold)
            + "E"
            + str(function.low_exponent)
            + ","
            + str(self.get_sf_assignment_val(function.circuit_assignment))
        )

    def get_switching_functions_status(self):
        """Returns statuses of switching functions

        Returns:
            a dictionary of 6 Enum members (SFStatus.ON/SFStatus.OFF) corresponding to each switching function
        """
        return self.get_sf_status_val(self._device.switching_functions_status)

    def get_pressure(self, channel):
        """Gets the pressure for a channel.

        Args:
            channel (Enum member): Enum readstate pressure channel. E.g. Readstate.A1.

        Returns:
            String: Device status and pressure from the channel.
        """
        pressure_suffix = "pressure_{}".format(self.get_readstate_val(channel).lower())
        status_suffix = "pressure_status_{}".format(self.get_readstate_val(channel).lower())
        pressure = getattr(self._device, pressure_suffix)
        status = getattr(self._device, status_suffix)
        return "{},{}".format(self.get_channel_status_val(status), pressure)

    def get_error_status(self):
        """Gets the device error status.

        Returns:
            String: (0000|1000|0100|0010|0001) four-character error status code
        """
        return self.get_error_status_val(self.device.error_status)


class Tpg300StreamInterface(Tpgx00StreamInterfaceBase, StreamInterface):
    protocol = "tpg300"

    class SFStatus300(Enum):
        OFF = 0
        ON = 1

    class Units300(Enum):
        hPascal = "Invalid unit"
        mbar = 1
        Torr = 2
        Pa = 3
        Micron = "Invalid unit"
        Volt = "Invalid unit"
        Ampere = "Invalid unit"

    class ChannelStatus300(Enum):
        DATA_OK = 0
        UNDERRANGE = 1
        OVERRANGE = 2
        POINT_ERROR = 3
        POINT_OFF = 4
        NO_HARDWARE = 5

    class SFAssignment300(Enum):
        OFF = 0
        A1 = 1
        A2 = 2
        B1 = 3
        B2 = 4
        A1_SELF_MON = 5
        A2_SELF_MON = 6
        B1_SELF_MON = 7
        B2_SELF_MON = 8
        ON = "Invalid assignment"

    class ErrorStatus300(Enum):
        NO_ERROR = "0000"
        DEVICE_ERROR = "1000"
        NO_HARDWARE = "0100"
        INVALID_PARAM = "0010"
        SYNTAX_ERROR = "0001"

    class ReadState300(Enum):
        A1 = "A1"
        A2 = "A2"
        B1 = "B1"
        B2 = "B2"
        UNI = "UNI"
        UNI0 = "Invalid command"
        UNI1 = "UNI1"
        UNI2 = "UNI2"
        UNI3 = "UNI3"
        UNI4 = "Invalid command"
        UNI5 = "Invalid command"
        UNI6 = "Invalid command"
        F1 = "F1"
        F2 = "F2"
        F3 = "F3"
        F4 = "F4"
        FA = "FA"
        FB = "FB"
        FS1 = "FS1"
        FS2 = "FS2"
        FS3 = "FS3"
        FS4 = "FS4"
        FSA = "FSA"
        FSB = "FSB"
        SPS = "SPS"

    def get_sf_status_val(self, status_enums):
        translated_vals = [
            str(self.SFStatus300[status.name].value) for status in status_enums.values()
        ]
        return translated_vals

    def get_units_val(self, unit_enum):
        return self.Units300[unit_enum.name].value

    def get_units_enum(self, unit_num):
        return self.Units300(unit_num)

    def get_channel_status_val(self, status_enum):
        return self.ChannelStatus300[status_enum.name].value

    def get_sf_assignment_name(self, assignment_num):
        return self.SFAssignment300(assignment_num).name

    def get_sf_assignment_val(self, assignment_enum):
        return self.SFAssignment300[assignment_enum.name].value

    def get_error_status_val(self, error_enum):
        return self.ErrorStatus300[error_enum.name].value

    def get_readstate_enum(self, state_str):
        return self.ReadState300(state_str)

    def get_readstate_val(self, readstate_enum):
        return self.ReadState300[readstate_enum.name].value


class Tpg500StreamInterface(Tpgx00StreamInterfaceBase, StreamInterface):
    protocol = "tpg500"

    class SFStatus500(Enum):
        OFF = 0
        ON = 1

    class Units500(Enum):
        hPascal = 0
        mbar = 1
        Torr = 2
        Pa = 3
        Micron = 4
        Volt = 5
        Ampere = 6

    class ChannelStatus500(Enum):
        DATA_OK = 0
        UNDERRANGE = 1
        OVERRANGE = 2
        POINT_ERROR = 3
        POINT_OFF = 4
        NO_HARDWARE = 5

    class SFAssignment500(Enum):
        OFF = 0
        A1 = 1
        A2 = 2
        B1 = 3
        B2 = 4
        A1_SELF_MON = "Invalid assignment"
        A2_SELF_MON = "Invalid assignment"
        B1_SELF_MON = "Invalid assignment"
        B2_SELF_MON = "Invalid assignment"
        ON = 5

    class ErrorStatus500(Enum):
        NO_ERROR = "0000"
        DEVICE_ERROR = "1000"
        NO_HARDWARE = "0100"
        INVALID_PARAM = "0010"
        SYNTAX_ERROR = "0001"

    class ReadState500(Enum):
        A1 = "a1"
        A2 = "a2"
        B1 = "b1"
        B2 = "b2"
        UNI = "UNI"
        UNI0 = "UNI0"
        UNI1 = "UNI1"
        UNI2 = "UNI2"
        UNI3 = "UNI3"
        UNI4 = "UNI4"
        UNI5 = "UNI5"
        UNI6 = "UNI6"
        F1 = "F1"
        F2 = "F2"
        F3 = "F3"
        F4 = "F4"
        FA = "Invalid command"
        FB = "Invalid command"
        FS1 = "FS1"
        FS2 = "FS2"
        FS3 = "FS3"
        FS4 = "FS4"
        FSA = "Invalid command"
        FSB = "Invalid command"
        SPS = "SPS"

    def get_sf_status_val(self, status_enums):
        translated_vals = [
            str(self.SFStatus500[status.name].value) for status in status_enums.values()
        ]
        return translated_vals

    def get_units_val(self, unit_enum):
        return self.Units500[unit_enum.name].value

    def get_units_enum(self, unit_num):
        return self.Units500(unit_num)

    def get_channel_status_val(self, status_enum):
        return self.ChannelStatus500[status_enum.name].value

    def get_sf_assignment_name(self, assignment_num):
        return self.SFAssignment500(assignment_num).name

    def get_sf_assignment_val(self, assignment_enum):
        return self.SFAssignment500[assignment_enum.name].value

    def get_error_status_val(self, error_enum):
        return self.ErrorStatus500[error_enum.name].value

    def get_readstate_enum(self, state_str):
        return self.ReadState500(state_str)

    def get_readstate_val(self, readstate_enum):
        return self.ReadState500[readstate_enum.name].value

    def get_thresholds_readstate(self, readstate):
        """Helper method for getting thresholds of a function all in one string based on current readstate.

        Args:
            readstate: (ReadState member) the current read state
        Returns:
            a string containing the lower and higher threshold, the switching f-n assignment and the
            ON-timer value.
        """
        function = self.get_threshold(self.get_readstate_val(readstate))
        return (
            str(function.high_threshold)
            + "E"
            + str(function.high_exponent)
            + ","
            + str(function.low_threshold)
            + "E"
            + str(function.low_exponent)
            + ","
            + str(self.get_sf_assignment_val(function.circuit_assignment))
            + ","
            + str(self._device.on_timer)
        )
