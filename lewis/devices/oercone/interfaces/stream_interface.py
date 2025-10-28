from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.constants import ACK, ENQ

from ..device import ReadState, Units


@has_log
class OerconeStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("handle_enquiry").escape(ENQ).build(),
        CmdBuilder("acknowledge_pressure").escape("PR1").eos().build(),
        CmdBuilder("acknowledge_measurement_unit").escape("UNI").eos().build(),
        CmdBuilder("acknowledge_set_measurement_unit")
        .escape("UNI,")
        .arg("0|1|2|3", argument_mapping=int)
        .eos()
        .build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        """Prints and logs an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            String: The error string.
        """
        err_string = 'command was: "{}", error was: {}: {}\n'.format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    def handle_enquiry(self):
        """Handles an enquiry using the last command sent.

        Returns:
            String: Channel pressure if last command was in channels.
            String: Returns the devices current units if last command is 'UNI'.
            None: Sets the devices units to 1,2, or 3 if last command is 'UNI{}' where {} is 1, 2 or 3
                respectively.
            None: Last command unknown.
        """
        self.log.info("Mode: {}".format(self._device._read_state.name))

        if self._device._read_state.name == "PR1":
            return self.get_pressure()
        elif self._device._read_state.name == "UNI":
            return self.get_measurement_unit()
        else:
            self.log.info(
                "Last command was unknown. Current readstate is {}.".format(
                    self._device._read_state
                )
            )
            print(
                "Last command was unknown. Current readstate is {}.".format(
                    self._device._read_state
                )
            )

    def acknowledge_pressure(self):
        """Acknowledges a request to get the pressure and stores the request.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device._read_state = ReadState["PR1"]
        return ACK

    def acknowledge_measurement_unit(self):
        """Acknowledge that the request to get the units was received.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device._read_state = ReadState["UNI"]
        return ACK

    def acknowledge_set_measurement_unit(self, units):
        """Acknowledge that the request to set the units was received.

        Args:
            units (integer): Takes the value 1, 2 or 3.

        Returns:
            ASCII acknowledgement character (0x6).
        """
        self._device._read_state = ReadState["UNI"]
        self._device.measurement_unit = Units(units)
        return ACK

    def get_pressure(self):
        """Gets the pressure for the device.

        Returns:
            String: Pressure from the channel.
        """
        return "0,{}".format(self._device.pressure)

    def get_measurement_unit(self):
        """Gets the units of the device.

        Returns:
            Name of the units.
        """
        return "{}".format(self._device.measurement_unit.value)

    def set_measurement_unit(self, units):
        """Sets the units on the device.

        Args:
            units (Units member): Units to be set

        Returns:
            None
        """
        self._device.measurement_unit = Units(units)
