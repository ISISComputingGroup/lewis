from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder

PREFIXES = [
    "",  # 0
    "\r\n",  # 1
    "\r\n  ",  # 2
    "\r\n01:23:45 ",  # 3
    "\r\n -------> ",  # 4
    ", ",  # 5
]


@has_log
class HlgStreamInterface(StreamInterface):
    """Stream interface for the serial port"""

    commands = {
        CmdBuilder("get_level").escape("PM").build(),
        CmdBuilder("set_verbosity").escape("CV").int().build(),
        CmdBuilder("set_prefix").escape("CP").int().build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        """If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    def set_verbosity(self, verbosity):
        """Set the verbosity of the output from the device

        Args:
            verbosity: 0 normal, 1 labview style (more verbose)

        Returns: confirmation message

        """
        if verbosity not in [0, 1]:
            raise AssertionError("Verbosity must be 0 or 1 was '{}'".format(verbosity))
        self._device.verbosity = verbosity
        if verbosity == 0:
            out_verbose = "Normal"
        else:
            out_verbose = "labVIEW"
        return self._format_output("CV{0}".format(verbosity), "Verbose=", out_verbose)

    def set_prefix(self, prefix):
        """Set the prefix the device returns
        Args:
            prefix: prefix id 0-5 see PREFIXES for details

        Returns: confirmation message

        """
        if not 0 <= prefix < len(PREFIXES):
            raise AssertionError(
                "Prefix must be between 0 and {1} '{0}'".format(prefix, len(PREFIXES))
            )
        self._device.prefix = prefix
        return self._format_output("CP{0}".format(prefix), "Verbose=", str(prefix))

    def get_level(self):
        """Gets the current level

        Returns: level in correct units or None if no level is set

        """
        if self._device.level is None:
            return None
        else:
            return self._format_output(
                "PM", "Probe value=", "{level:.3f} mm".format(level=self._device.level)
            )

    def _format_output(self, echo, verbose_prefix, data):
        """Format the output of a command depending on verbosity and prefix settings of device
        Args:
            echo: string to echo back to user
            verbose_prefix: prefix for value in normal verbose mode
            data: data to output

        Returns: formatted output from command

        """
        output_string = echo
        output_string += PREFIXES[self._device.prefix]
        if self._device.verbosity == 0:
            output_string += verbose_prefix
        output_string += data
        return output_string
