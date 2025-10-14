"""Stream interface for the SP2xx device.
"""

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder, string_arg
from lewis.utils.replies import conditional_reply

from ..util_classes import RunStatus
from ..util_constants import DIRECTIONS

ALLOWED_VOLUME_UNITS = ["ul", "ml"]
ALLOWED_RATE_UNITS = ["ul/m", "ml/m", "ul/h", "ml/h"]

if_connected = conditional_reply("connected")


def if_error(f):
    """Decorator that executes f if the device has no errors on it and returns the error prompt otherwise.

    Args:
        f: function to be executed if the device has no error.

    Returns:
       The value of f(*args) if the device has no error and "\r\nE" otherwise.
    """

    def _wrapper(*args):
        error = getattr(args[0], "_device").last_error.value
        if error == 0:
            result = f(*args)
        else:
            result = "\r\nE"
        return result

    return _wrapper


@has_log
class Sp2XXStreamInterface(StreamInterface):
    """Stream interface for the serial port.
    """

    def __init__(self):
        super(Sp2XXStreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.start).escape("run").eos().build(),
            CmdBuilder(self.stop).escape("stop").eos().build(),
            CmdBuilder(self.get_run_status).escape("run?").eos().build(),
            CmdBuilder(self.get_error_status).escape("error?").eos().build(),
            CmdBuilder(self.set_mode).escape("mode ").arg("i/w|w/i|i|w|con").eos().build(),
            CmdBuilder(self.get_mode).escape("mode?").eos().build(),
            CmdBuilder(self.get_direction).escape("dir?").eos().build(),
            CmdBuilder(self.reverse_direction).escape("dir rev").eos().build(),
            CmdBuilder(self.get_diameter).escape("dia?").eos().build(),
            CmdBuilder(self.set_diameter).escape("dia ").float().eos().build(),
            CmdBuilder(self.set_volume_or_rate)
            .arg("vol|rate")
            .char()
            .escape(" ")
            .float(string_arg)
            .escape(" ")
            .string()
            .eos()
            .build(),
            CmdBuilder(self.get_volume_or_rate).arg("vol|rate").char().escape("?").eos().build(),
        }

    out_terminator = ""
    in_terminator = "\r"

    _return = "\r\n"
    Infusion = "\r\n>"
    Withdrawal = "\r\n<"
    Stopped = "\r\n:"

    def handle_error(self, request, error):
        """Prints an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            None.
        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

        print("An error occurred at request {}: {}".format(request, error))

    @if_error
    @if_connected
    def start(self):
        """Starts the device running to present settings if it is not running.

        Returns:

        """
        if self._device.running is False:
            if self._device.direction == DIRECTIONS["I"]:
                self._device.start_device()
                return self.Infusion
            elif self._device.direction == DIRECTIONS["W"]:
                self._device.start_device()
                return self.Withdrawal
            else:
                print(
                    "An error occurred when trying to run the device. The device's running state is \
                    is {}.".format(self._device.running_direction)
                )

    @if_error
    @if_connected
    def get_run_status(self):
        """Gets the run status of the pump.

        Returns:
            "\r\n:" : If the device is not running.
            "\r\n>" : Prompt saying the device's run direction is infusing.
            "\r\n<" : Prompt saying the device's run direction is withdrawing.
        """
        if self._device.running_status == RunStatus.Infusion:
            return self.Infusion
        elif self._device.running_status == RunStatus.Withdrawal:
            return self.Withdrawal
        elif self._device.running_status == RunStatus.Stopped:
            return self.Stopped
        else:
            print("An error occurred when trying to run the device.")

    @if_error
    @if_connected
    def stop(self):
        """Stops the device running.

        Returns:
            "\r\n:" : stopped prompt
        """
        self._device.stop_device()
        return self.Stopped

    @if_connected
    def get_error_status(self):
        """Gets the error status from the device and returns the error value and run status.

        Returns:
            \r\n%i\r{} where %i is the error_type value and {} the run status.
        """
        last_error = self._device.last_error
        current_status = None

        if self._device.running_status == RunStatus.Infusion:
            current_status = self.Infusion
        elif self._device.running_status == RunStatus.Withdrawal:
            current_status = self.Withdrawal
        elif self._device.running_status == RunStatus.Stopped:
            current_status = self.Stopped

        return "{}{}{}".format(self._return, last_error.value, current_status)

    @if_error
    @if_connected
    def set_mode(self, mode_symbol):
        """Sets the mode of the device.

        Args:
            mode_symbol: symbol to change the mode setting

        Returns:
            run_status
        """
        self._device.set_mode(mode_symbol)
        return self.stop()

    @if_error
    @if_connected
    def get_mode(self):
        """Gets the mode of the device

        Returns:
            The mode the device is in and the run status.
            E.g. \r\nI\r\n: if the device is in infusion mode and stopped.
        """
        mode_response = self._device.mode.response
        run_status = self.get_run_status()
        return "{}{}{}".format(self._return, mode_response, run_status)

    @if_error
    @if_connected
    def get_direction(self):
        """Gets the direction of the device

        Returns:
            The direction the device is in and the run status.
            E.g. \r\nI\r: if the device in the infusion direction and stopped.
        """
        run_status = self.get_run_status()
        return "{}{}{}".format(self._return, self._device.direction.symbol, run_status)

    @if_error
    @if_connected
    def reverse_direction(self):
        """Attempt to reverse the direction of a running device.

        Returns:
            Run status if the device is running and in infusion or withdrawal mode.
            NA otherwise.
        """
        if self._device.reverse_direction():
            return self.get_run_status()
        else:
            return "{}NA{}".format(self._return, self.get_run_status())

    @if_error
    @if_connected
    def get_diameter(self):
        """Gets the diameter that the syringe is set to.

        Returns:
            float: Diameter of the syringe.
        """
        run_status = self.get_run_status()
        return "{}{}{}".format(self._return, self._device.diameter, run_status)

    def set_diameter(self, value):
        """Sets the diameter of the
        Returns:
            \r\nNA{}: If value is
        """
        if self._device.successfully_set_diameter(value):
            return "{}".format(self.Stopped)
        else:
            run_status = self.get_run_status()
            return "{}NA{}".format(self._return, run_status)

    @if_error
    @if_connected
    def set_volume_or_rate(self, vol_or_rate, vol_or_rate_type, value, units):
        """Set a volume or rate.

        Args:
            vol_or_rate: vol to set a volume, rate to set a rate, anything else is an error
            vol_or_rate_type: the type of the volume or rate, i for infusion, w for withdrawal, anything else
            is an error
            value:  value to set it too; of form nnnnn (0-9 and. won't accept number larger than 9999)
            units: units
        Returns:
            return string
        """
        run_status = self.get_run_status()
        if len(value) > 5:
            self.log.error("Value is too long: '{}' ".format(value))
            return "{}NA{}".format(self._return, run_status)
        actual_volume = float(value)

        if vol_or_rate == "vol":
            allowed_units = ALLOWED_VOLUME_UNITS
        else:
            allowed_units = ALLOWED_RATE_UNITS
        if units not in allowed_units:
            self.log.error("Units are unknown: '{}' ".format(units))
            return "{}NA{}".format(self._return, run_status)

        if vol_or_rate == "vol" and vol_or_rate_type == "i":
            self._device.infusion_volume_units = units
            self._device.infusion_volume = actual_volume
        elif vol_or_rate == "vol" and vol_or_rate_type == "w":
            self._device.withdrawal_volume_units = units
            self._device.withdrawal_volume = actual_volume
        elif vol_or_rate == "rate" and vol_or_rate_type == "i":
            self._device.infusion_rate_units = units
            self._device.infusion_rate = actual_volume
        elif vol_or_rate == "rate" and vol_or_rate_type == "w":
            self._device.withdrawal_rate_units = units
            self._device.withdrawal_rate = actual_volume
        else:
            self.log.error("command is not know: '{}{}' ".format(vol_or_rate, vol_or_rate_type))
            return "{}NA{}".format(self._return, run_status)

        return "{}".format(self.Stopped)

    @if_error
    @if_connected
    def get_volume_or_rate(self, vol_or_rate, vol_or_rate_type):
        """Get a volume or rate.

        Args:
            vol_or_rate: vol to set a volume, rate to set a rate, anything else is an error
            vol_or_rate_type: the type of the volume or rate, i for infusion, w for withdrawal, anything else
            is an error
        Returns:
            return string
        """
        run_status = self.get_run_status()

        if vol_or_rate == "vol" and vol_or_rate_type == "i":
            value = self._device.infusion_volume
            units = self._device.infusion_volume_units

        elif vol_or_rate == "vol" and vol_or_rate_type == "w":
            value = self._device.withdrawal_volume
            units = self._device.withdrawal_volume_units
        elif vol_or_rate == "rate" and vol_or_rate_type == "i":
            value = self._device.infusion_rate
            units = self._device.infusion_rate_units
        elif vol_or_rate == "rate" and vol_or_rate_type == "w":
            value = self._device.withdrawal_rate
            units = self._device.withdrawal_rate_units
        else:
            self.log.error("Command is not know: '{}{}?' ".format(vol_or_rate, vol_or_rate_type))
            return "{}NA{}".format(self._return, run_status)

        if value < 10.0:
            format_string = "{:5.3f} {}"
        elif value < 100.0:
            format_string = "{:5.2f} {}"
        elif value < 1000.0:
            format_string = "{:5.1f} {}"
        else:
            format_string = "{:5f} {}"

        volume_as_string = format_string.format(value, units)

        return "{}{}{}".format(self._return, volume_as_string, self.get_run_status())
