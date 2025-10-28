import abc

from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder

ACK = chr(6)


class TpgStreamInterfaceBase(object, metaclass=abc.ABCMeta):
    """Stream interface for the serial port for either a TPG26x or TPG36x."""

    _last_command = None

    @abc.abstractmethod
    def acknowledgement(self):
        """Returns a string which is the device's "acknowledgement" message."""

    @abc.abstractmethod
    def output_terminator(self):
        """A terminator to add to every reply except acknowledgement messages."""

    commands = {
        CmdBuilder("acknowledge_pressure").escape("PRX").build(),
        CmdBuilder("acknowledge_units").escape("UNI").build(),
        CmdBuilder("set_units").escape("UNI").arg("{0|1|2}").build(),
        CmdBuilder("handle_enquiry").enq().build(),
    }

    def handle_error(self, request, error):
        """If command is not recognised print and error.

        :param request: requested string
        :param error: problem
        :return:
        """
        print("An error occurred at request " + repr(request) + ": " + repr(error))

    def acknowledge_pressure(self):
        """Acknowledge that the request for current pressure was received.

        :return: ASCII acknowledgement character (0x6)
        """
        self._last_command = "PRX"
        return self.acknowledgement()

    def acknowledge_units(self):
        """Acknowledge that the request for current units was received.

        :return: ASCII acknowledgement character (0x6)
        """
        self._last_command = "UNI"
        return self.acknowledgement()

    def handle_enquiry(self):
        """Handle an enquiry using the last command sent.

        :return:
        """
        if self._last_command == "PRX":
            return "{}{}".format(self.get_pressure(), self.output_terminator())
        elif self._last_command == "UNI":
            return "{}{}".format(self.get_units(), self.output_terminator())
        else:
            print("Last command was unknown: " + repr(self._last_command))

    def get_pressure(self):
        """Get the current pressure of the TPG26x.

        Returns: a string with pressure and error codes
        """
        return "{},{},{},{}{}".format(
            self._device.error1,
            self._device.pressure1,
            self._device.error2,
            self._device.pressure2,
            self.output_terminator(),
        )

    def get_units(self):
        """Get the current units of the TPG26x.

        Returns: a string representing the units
        """
        return self._device.units

    def set_units(self, units):
        """Set the units of the TPG26x.

        :param units: the unit flag to change the units to
        """
        if self._last_command is None:
            self._last_command = "UNI"
            return self.acknowledgement()

        self._device.units = units
        self._last_command = None


class Tpg36xStreamInterface(TpgStreamInterfaceBase, StreamInterface):
    protocol = "tpg36x"
    in_terminator = ""
    out_terminator = ""

    def acknowledgement(self):
        return "{}\r\n".format(ACK)

    def output_terminator(self):
        return "\r"


class Tpg361StreamInterface(Tpg36xStreamInterface, StreamInterface):
    protocol = "tpg361"

    def get_pressure(self):
        return "{},{}{}".format(
            self._device.error1, self._device.pressure1, self.output_terminator()
        )


class Tpg26xStreamInterface(TpgStreamInterfaceBase, StreamInterface):
    protocol = "tpg26x"

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def acknowledgement(self):
        return "{}".format(ACK)

    # No "additional" terminator (just uses the lewis one defined above).
    def output_terminator(self):
        return ""
