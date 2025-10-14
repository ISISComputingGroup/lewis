from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder


@has_log
class Lakeshore460StreamInterface(StreamInterface):
    """Stream interface for the serial port
    """

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    commands = {
        # get_multicmds splits commands by ';' if multiple command strings are received
        CmdBuilder("get_multicmds", arg_sep="").arg("[^;]+").escape(";").arg(".*").build(),
        CmdBuilder("get_idn").escape("*IDN?").build(),
        CmdBuilder("get_source").escape("VSRC?").build(),
        CmdBuilder("set_source").escape("VSRC ").digit().build(),
        CmdBuilder("get_channel").escape("CHNL?").build(),
        CmdBuilder("set_channel").escape("CHNL ").arg("X|Y|Z|V").eos().build(),
        CmdBuilder("get_magnetic_field_reading").escape("FIELD?").build(),
        CmdBuilder("get_magnetic_field_reading_multiplier").escape("FIELDM?").build(),
        CmdBuilder("get_max_hold_reading").escape("MAXR?").build(),
        CmdBuilder("get_max_hold_reading_multiplier").escape("MAXRM?").build(),
        CmdBuilder("get_relative_mode_reading").escape("RELR?").build(),
        CmdBuilder("get_relative_mode_multiplier").escape("RELRM?").build(),
        CmdBuilder("get_unit").escape("UNIT?").build(),
        CmdBuilder("set_unit").escape("UNIT ").arg("G|T").build(),
        CmdBuilder("get_ac_dc_mode").escape("ACDC?").build(),
        CmdBuilder("set_ac_dc_mode").escape("ACDC ").arg("0|1").build(),
        CmdBuilder("get_prms_reading").escape("PRMS?").build(),
        CmdBuilder("set_prms_reading").escape("PRMS ").arg("0|1").build(),
        CmdBuilder("set_filter_status").escape("FILT ").arg("0|1").build(),
        CmdBuilder("get_filter_status").escape("FILT?").build(),
        CmdBuilder("set_relative_mode_status").escape("REL ").arg("0|1").build(),
        CmdBuilder("get_relative_mode_status").escape("REL?").build(),
        CmdBuilder("get_relative_setpoint").escape("RELS?").build(),
        CmdBuilder("set_relative_setpoint").escape("RELS ").float().build(),
        CmdBuilder("get_relative_setpoint_multiplier").escape("RELSM?").build(),
        CmdBuilder("set_auto_mode_status").escape("AUTO ").arg("0|1").build(),
        CmdBuilder("get_auto_mode_status").escape("AUTO?").build(),
        CmdBuilder("set_max_hold_status").escape("MAX ").arg("0|1").build(),
        CmdBuilder("get_max_hold_status").escape("MAX?").build(),
        CmdBuilder("get_channel_status").escape("ONOFF?").build(),
        CmdBuilder("set_channel_status").escape("ONOFF ").arg("0|1").build(),
        CmdBuilder("get_filter_windows").escape("FWIN?").build(),
        CmdBuilder("set_filter_windows").escape("FWIN ").int().build(),
        CmdBuilder("set_filter_points").escape("FNUM ").int().build(),
        CmdBuilder("get_filter_points").escape("FNUM?").build(),
        CmdBuilder("get_manual_range").escape("RANGE?").build(),
        CmdBuilder("set_manual_range").escape("RANGE ").int().build(),
    }

    def handle_error(self, request, error):
        self.log.error("An error occurred at request" + repr(request) + ": " + repr(error))
        print("An error occurred at request" + repr(request) + ": " + repr(error))

    def get_idn(self):
        return "{0}".format(self._device.idn)

    def set_source(self, source):
        self._device.source = source

    def get_source(self):
        return "{0}".format(self._device.source)

    def set_channel(self, channel):
        self._device.channel = channel

    def get_channel(self):
        return "{0}".format(self._device.channel)

    def get_magnetic_field_reading(self):
        field_reading = self._device.channels[self.get_channel()].field_reading
        multiplier = self._device.channels[self.get_channel()].field_multiplier

        # Update max_hold_reading if field_reading is larger
        if field_reading > self._device.channels[self.get_channel()].max_hold_reading:
            self._device.channels[self.get_channel()].max_hold_reading = field_reading
            self._device.channels[self.get_channel()].max_hold_reading_multiplier = multiplier

        return "{0}".format(self._device.channels[self.get_channel()].field_reading)

    def get_magnetic_field_reading_multiplier(self):
        return "{0}".format(self._device.channels[self.get_channel()].field_multiplier)

    def get_max_hold_reading(self):
        return "{0}".format(self._device.channels[self.get_channel()].max_hold_reading)

    def get_max_hold_reading_multiplier(self):
        return "{0}".format(self._device.channels[self.get_channel()].max_hold_multiplier)

    def get_relative_mode_reading(self):
        return "{0}".format(self._device.channels[self.get_channel()].rel_mode_reading)

    def get_relative_mode_multiplier(self):
        return "{0}".format(self._device.channels[self.get_channel()].rel_mode_multiplier)

    def get_unit(self):
        return "{0}".format(self._device.unit)

    def set_unit(self, unit):
        # Convert values if required
        if self._device.unit == "T":
            if unit == "G":
                self._device.convert_units(10000)
        if self._device.unit == "G":
            if unit == "T":
                self._device.convert_units(0.0001)
        self._device.unit = unit

    def get_ac_dc_mode(self):
        return "{0}".format(self._device.channels[self.get_channel()].mode)

    def set_ac_dc_mode(self, mode):
        self._device.channels[self.get_channel()].mode = mode

    def get_prms_reading(self):
        return "{0}".format(self._device.channels[self.get_channel()].prms)

    def set_prms_reading(self, prms):
        self._device.channels[self.get_channel()].prms = prms

    def get_filter_status(self):
        return "{0}".format(self._device.channels[self.get_channel()].filter_status)

    def set_filter_status(self, filter):
        self._device.channels[self.get_channel()].filter_status = filter

    def set_relative_mode_status(self, rel_mode):
        self._device.channels[self.get_channel()].rel_mode_status = rel_mode

    def get_relative_mode_status(self):
        return_val = "{0}".format(self._device.channels[self.get_channel()].rel_mode_status)
        return return_val

    def set_auto_mode_status(self, auto_mode_status):
        self._device.channels[self.get_channel()].auto_mode_status = auto_mode_status

    def get_auto_mode_status(self):
        return "{0}".format(self._device.channels[self.get_channel()].auto_mode_status)

    def set_max_hold_status(self, max_hold_status):
        self._device.channels[self.get_channel()].max_hold_status = max_hold_status

    def get_max_hold_status(self):
        return "{0}".format(self._device.channels[self.get_channel()].max_hold_status)

    def get_channel_status(self):
        return "{0}".format(self._device.channels[self.get_channel()].channel_status)

    def set_channel_status(self, status):
        self._device.channels[self.get_channel()].channel_status = status

    def get_filter_windows(self):
        return "{0}".format(self._device.channels[self._device.channel].filter_windows)

    def set_filter_windows(self, percentage):
        self._device.channels[self.get_channel()].filter_windows = percentage

    def get_filter_points(self):
        return "{0}".format(self._device.channels[self.get_channel()].filter_points)

    def set_filter_points(self, points):
        self._device.channels[self.get_channel()].filter_points = points

    def set_manual_range(self, range):
        self._device.channels[self.get_channel()].manual_range = range

    def get_manual_range(self):
        return "{0}".format(self._device.channels[self.get_channel()].manual_range)

    def get_relative_setpoint(self):
        return self._device.channels[self.get_channel()].relative_setpoint

    def set_relative_setpoint(self, rel_setpoint):
        self._device.channels[self.get_channel()].relative_setpoint = rel_setpoint

    def get_relative_setpoint_multiplier(self):
        return self._device.channels[self.get_channel()].relative_setpoint_multiplier

    def get_multicmds(self, command, other_commands):
        """As the protocol file sends multiple commands (set Channel; request channel PV),
        these methods split up the commands and process both.
        """
        replies = []
        for cmd_to_find in [command, other_commands]:
            cmd_to_find = bytes(cmd_to_find, "utf-8")
            self.log.info("Processing {} from combined command".format(cmd_to_find))
            reply = self._process_part_command(cmd_to_find)
            if reply is not None:
                replies.append(self._process_part_command(cmd_to_find))
        return self.out_terminator.join(replies)

    def _process_part_command(self, cmd_to_find):
        for cmd in self.bound_commands:
            if cmd.can_process(cmd_to_find):
                return cmd.process_request(cmd_to_find)
        self.log.info("Error, unable to find command: {}".format(cmd_to_find))
