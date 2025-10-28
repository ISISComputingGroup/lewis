import random
from collections import OrderedDict
from functools import wraps

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import DefaultState


def truncate_if_set(f):
    """Truncates the decorated function's string output if truncated_output is True"""

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        output = f(self, *args, **kwargs)

        if self.truncated_output:
            output = output[: int(round(len(output) / 2.0))]

        return output

    return wrapper


@has_log
def fake_auto_send(f):
    """Changes the decorated functions's string output to a simulate a device in auto-send mode"""

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        output = f(self, *args, **kwargs)

        if self.auto_send:
            output = "TG,{:02d},+FFFFFFF".format(random.randint(1, 4))

        return output

    return wrapper


@has_log
class SimulatedKynctm3K(StateMachineDevice):
    INPUT_MODES = ("R0", "R1", "Q0")

    def _initialize_data(self):
        """Initialize all of the device's attributes.

        OUT_values contains the measurement values to be returned. A False value is considered to not
        be in the program, and will not be returned.
        """
        self.OUT_values = None
        self.truncated_output = False
        self.auto_send = False
        self.input_mode = "R0"

        pass

    def reset_device(self):
        """Resets the device to a known state. This can be confirmed when the OUT channels equal -256.0

        Returns: None

        """
        self._initialize_data()
        self.OUT_values = ["off"] * 16

        return None

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    def set_autosend_status(self, new_state):
        """Sets the autosend status between True (autosend on) and False (autosend off)

        Args:
            new_state: Boolean, the new autosend state

        Returns:
            A string acknowledging the status change, or an error if the device is in the wrong state to change the setting

        """
        try:
            assert isinstance(new_state, int)
        except AssertionError:
            return "ER,SW,08"

        if self.input_mode in ("R0", "R1"):
            # Cannot change the autosend in this input mode
            return "ER,SW,01"

        else:
            self.auto_send = bool(new_state)
            return "SW,EA"

    def set_input_mode(self, new_state):
        """Changes the state of the device to a measurment screen (R0/R1) or a RS232C comms mode (Q0)

        Args:
            new_state: String, denoting measurement screen (R0/R1) or RS232C mode (Q0)

        Returns:
            new_state: String. Either the name of the new state, or an error code if the new state was not recognised

        """
        if new_state in self.INPUT_MODES:
            self.input_mode = new_state
            return new_state
        else:
            return "ER,{:.2},01".format(new_state)

    def parse_status(self, output_setting):
        """Converts the status for one OUT channel to a formatted string
        Args:
            output_setting: String or float. If float, then output is on. If off or out_of_bounds, then a formatted string will be returned

        Returns:
            OUT_string: String. Contains the measurement value if on, or XXXXXXXX/FFFFFFF as appropriate if off or out of range

        """
        out_of_range_return = "FFFFFFF"
        off_return = "XXXXXXXX"

        if output_setting == "off":
            return off_return

        elif output_setting == "out_of_range":
            # Add a random sign to the out of range string
            sign = random.sample(("+", "-"), 1)[0]
            return sign + out_of_range_return

        elif type(output_setting) is float:
            return "{:+08.3f}".format(output_setting)

        else:
            return off_return

    @fake_auto_send
    @truncate_if_set
    def format_output_data(self):
        """Recalls and formats the measurement values

        Returns:
            A string containing the measurement values for the current program, formatted as per the user manual

        """
        if self.OUT_values is None:
            return None
        else:
            channel_strings = [
                "MM,1111111111111111",
            ]
            for channel, output_value in enumerate(self.OUT_values):
                # Only return output if the OUT value is in the program
                channel_strings.append(self.parse_status(output_value))

        return ",".join(channel_strings)
