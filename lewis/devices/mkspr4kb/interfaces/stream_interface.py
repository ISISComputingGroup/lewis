from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


class MKS_PR4000B_StreamInterface(StreamInterface):
    def __init__(self):
        super(MKS_PR4000B_StreamInterface, self).__init__()

        self.commands = {
            CmdBuilder("get_value").escape("AV").int().eos().build(),
            CmdBuilder("get_valve_status").escape("?VL").int().eos().build(),
            CmdBuilder("set_valve_status")
            .escape("VL")
            .int()
            .escape(",")
            .enum("ON", "OFF")
            .eos()
            .build(),
            CmdBuilder("get_relay_status").escape("?RL").int().eos().build(),
            CmdBuilder("set_relay_status")
            .escape("RL")
            .int()
            .escape(",")
            .enum("ON", "OFF")
            .eos()
            .build(),
            CmdBuilder("get_formula_relay").escape("?FR").int().eos().build(),
            CmdBuilder("set_formula_relay")
            .escape("FR")
            .int()
            .escape(",")
            .any()
            .eos()
            .build(),
            CmdBuilder("get_remote_mode").escape("?RT").eos().build(),
            CmdBuilder("set_remote_mode")
            .escape("RT")
            .escape(",")
            .enum("ON", "OFF")
            .eos()
            .build(),
            CmdBuilder("get_external_input").escape("EX").int().eos().build(),
            CmdBuilder("get_status").escape("ST").eos().build(),
            CmdBuilder("set_range")
            .escape("RG")
            .int()
            .escape(",")
            .float()
            .escape(",")
            .int()
            .eos()
            .build(),
            CmdBuilder("get_range").escape("?RG").int().eos().build(),
            CmdBuilder("get_id").escape("?ID").eos().build(),
        }

        # These get appended to the list of commands above - just map command syntax against emulator property
        numeric_get_and_set_commands = {
            "SP": "setpoint",
            "GN": "gain",
            "OF": "offset",
            "RO": "rtd_offset",
            "IN": "input_range",
            "OT": "output_range",
            "EI": "ext_input_range",
            "EO": "ext_output_range",
            "SC": "scale",
            "UL": "upper_limit",
            "LL": "lower_limit",
            "SM": "signalmode",  # As far as the emulator is concerned, this is an int. IOC treats is as enum.
            "LM": "limitmode",  # As far as the emulator is concerned, this is an int. IOC treats is as enum.
        }

        getter_factory, setter_factory = self._get_getter_and_setter_factories()

        for command_name, emulator_name in numeric_get_and_set_commands.items():
            self.commands.update(
                {
                    CmdBuilder(setter_factory(emulator_name))
                    .escape(command_name)
                    .int()
                    .escape(",")
                    .float()
                    .eos()
                    .build(),
                    CmdBuilder(getter_factory(emulator_name))
                    .escape("?{}".format(command_name))
                    .int()
                    .eos()
                    .build(),
                }
            )

    def _get_getter_and_setter_factories(self):
        """Returns a pair of functions (getter_factory, setter_factory) which can generate appropriate attribute getters
        and setters for a given property name.

        For example:
        >>> getter_factory("foo")
        will generate the getter accessing
        >>> self.device.channels[chan].foo
        where
        >>> chan
        is one of the captured arguments to the getter.

        Factory methods are used to force the functions to bind correctly.
        """

        def getter_factory(name):
            def getter(chan):
                if not self.device.connected:
                    return None
                return "{:.2f}".format(getattr(self.device.channels[chan], name))

            return getter

        def setter_factory(name):
            def setter(chan, value):
                if not self.device.connected:
                    return None
                setattr(self.device.channels[chan], name, value)
                return ""

            return setter

        return getter_factory, setter_factory

    in_terminator = "\r"
    out_terminator = "\r"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    @if_connected
    def get_value(self, chan):
        return "{:.2f}".format(self.device.channels[chan].setpoint)

    @if_connected
    def get_valve_status(self, chan):
        return "ON" if self.device.channels[chan].valve_enabled else "OFF"

    @if_connected
    def set_valve_status(self, chan, status):
        self.device.channels[chan].valve_enabled = status == "ON"
        return ""

    @if_connected
    def get_relay_status(self, chan):
        return "ON" if self.device.channels[chan].relay_enabled else "OFF"

    @if_connected
    def set_relay_status(self, chan, status):
        self.device.channels[chan].relay_enabled = status == "ON"
        return ""

    @if_connected
    def get_formula_relay(self, chan):
        return self.device.channels[chan].formula_relay

    @if_connected
    def set_formula_relay(self, chan, formula):
        self.device.channels[chan].formula_relay = formula
        return ""

    @if_connected
    def get_remote_mode(self):
        return "ON" if self.device.remote_mode else "OFF"

    @if_connected
    def set_remote_mode(self, mode):
        self.device.remote_mode = mode == "ON"
        return ""

    @if_connected
    def get_external_input(self, chan):
        return "{:.2f}".format(self.device.channels[chan].external_input)

    @if_connected
    def get_status(self):
        return "{:05d}".format(0)  # Return a constant here, just to keep IOC happy.

    @if_connected
    def get_range(self, chan):
        return "{:.2f},{:02d}".format(
            self.device.channels[chan].range, self.device.channels[chan].range_units
        )

    @if_connected
    def set_range(self, chan, range, units):
        self.device.channels[chan].range = range
        self.device.channels[chan].range_units = units
        return ""

    @if_connected
    def get_id(self):
        return "emulated_mks_pr4000"
