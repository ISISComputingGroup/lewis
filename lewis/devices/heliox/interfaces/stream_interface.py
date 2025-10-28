from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")

ISOBUS_PREFIX = "@1"
PRIMARY_DEVICE_NAME = "HelioxX"


class HelioxStreamInterface(StreamInterface):
    commands = {
        CmdBuilder("get_catalog").optional(ISOBUS_PREFIX).escape("READ:SYS:CAT").eos().build(),
        CmdBuilder("get_all_heliox_status")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .escape(PRIMARY_DEVICE_NAME)
        .escape(":HEL")
        .eos()
        .build(),
        CmdBuilder("get_heliox_temp")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .escape(PRIMARY_DEVICE_NAME)
        .escape(":HEL:SIG:TEMP")
        .eos()
        .build(),
        CmdBuilder("get_heliox_temp_sp_rbv")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .escape(PRIMARY_DEVICE_NAME)
        .escape(":HEL:SIG:TSET")
        .eos()
        .build(),
        CmdBuilder("get_heliox_stable")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .escape(PRIMARY_DEVICE_NAME)
        .escape(":HEL:SIG:H3PS")
        .eos()
        .build(),
        CmdBuilder("get_heliox_status")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .escape(PRIMARY_DEVICE_NAME)
        .escape(":HEL:SIG:STAT")
        .eos()
        .build(),
        CmdBuilder("set_heliox_setpoint")
        .optional(ISOBUS_PREFIX)
        .escape("SET:DEV:{}:HEL:SIG:TSET:".format(PRIMARY_DEVICE_NAME))
        .float()
        .escape("K")
        .eos()
        .build(),
        CmdBuilder("get_nickname")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .any()
        .escape(":NICK")
        .eos()
        .build(),
        CmdBuilder("get_channel_status")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .arg(r"[^:]*")
        .escape(":TEMP")
        .eos()
        .build(),
        CmdBuilder("get_channel_temp")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .arg(r"[^:]*")
        .escape(":TEMP:SIG:TEMP")
        .eos()
        .build(),
        CmdBuilder("get_channel_temp_sp")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .arg(r"[^:]*")
        .escape(":TEMP:LOOP:TSET")
        .eos()
        .build(),
        CmdBuilder("get_channel_heater_auto")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .arg(r"[^:]*")
        .escape(":TEMP:LOOP:ENAB")
        .eos()
        .build(),
        CmdBuilder("get_channel_heater_percentage")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:")
        .arg(r"[^:]*")
        .escape(":TEMP:LOOP:HSET")
        .eos()
        .build(),
        CmdBuilder("get_he3_sorb_stable")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:{}:HEL:SIG:SRBS".format(PRIMARY_DEVICE_NAME))
        .eos()
        .build(),
        CmdBuilder("get_he4_pot_stable")
        .optional(ISOBUS_PREFIX)
        .escape("READ:DEV:{}:HEL:SIG:H4PS".format(PRIMARY_DEVICE_NAME))
        .eos()
        .build(),
    }

    in_terminator = "\n"
    out_terminator = "\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return err_string

    @if_connected
    def get_all_heliox_status(self):
        """This function is used by the labview VI. In EPICS it is more convenient to ask for the parameters individually,
        so we don't use this large function which generates all of the possible status information.
        """
        return (
            "STAT:DEV:{}".format(PRIMARY_DEVICE_NAME)
            + ":HEL:LOWT:2.5000K"
            ":BT:0.0000K"
            ":NVCN:17.000mB"
            ":RCTD:10.000K"
            ":RCST:20.000K"
            ":NVHT:17.000mB"
            ":RCTE:10.000K"
            ":SRBH:15.000K"
            ":PE:3.5000K"
            ":RGNA:1.0000K"
            ":PCT:2.0000K"
            ":SIG:H4PS:{}".format(
                "Stable" if self.device.temperature_channels["HE4POT"].stable else "Unstable"
            )
            + ":STAT:{}".format(self.device.status)
            + ":TEMP:{:.4f}K".format(self.device.temperature)
            + ":TSET:{:.4f}K".format(self.device.temperature_sp)
            + ":H3PS:{}".format("Stable" if self.device.temperature_stable else "Unstable")
            + ":SRBS:{}".format(
                "Stable" if self.device.temperature_channels["HE3SORB"].stable else "Unstable"
            )
            + ":SRBR:32.000K"
            ":SCT:3.0000K"
            ":NVLT:10.000mB"
        )

    @if_connected
    def get_catalog(self):
        """This is only needed by the LabVIEW driver - it is not used by EPICS."""
        return (
            "STAT:SYS:CAT"
            ":DEV:HelioxX:HEL"
            ":DEV:He3Sorb:TEMP"
            ":DEV:He4Pot:TEMP"
            ":DEV:HeLow:TEMP"
            ":DEV:HeHigh:TEMP"
        )

    @if_connected
    def get_nickname(self, arg):
        """Returns a fake nickname. This is only implemented to allow this emulator to be used with the existing
        labview driver, and the labview driver actually ignores the results (but not implementing the function causes
        an error).
        """
        return "STAT:DEV:{}:NICK:{}".format(arg, "FAKENICKNAME")

    @if_connected
    def set_heliox_setpoint(self, new_setpoint):
        self.device.temperature_sp = new_setpoint
        return "STAT:SET:DEV:HelioxX:HEL:SIG:TSET:{:.4f}K:VALID".format(new_setpoint)

    @if_connected
    def get_heliox_temp(self):
        return "STAT:DEV:HelioxX:HEL:SIG:TEMP:{:.4f}K".format(self.device.temperature)

    @if_connected
    def get_heliox_temp_sp_rbv(self):
        return "STAT:DEV:HelioxX:HEL:SIG:TSET:{:.4f}K".format(self.device.temperature_sp)

    @if_connected
    def get_heliox_stable(self):
        return "STAT:DEV:{}:HEL:SIG:H3PS:{}".format(
            PRIMARY_DEVICE_NAME,
            "Stable" if self.device.temperature_stable else "Unstable",
        )

    @if_connected
    def get_heliox_status(self):
        return "STAT:DEV:{}:HEL:SIG:STAT:{}".format(PRIMARY_DEVICE_NAME, self.device.status)

    @if_connected
    def get_channel_status(self, channel):
        temperature_channel = self.device.temperature_channels[channel.upper()]
        return (
            "STAT:DEV:{name}:TEMP"
            ":EXCT:TYPE:UNIP:MAG:0"
            ":STAT:40000000"
            ":NICK:MB1.T1"
            ":LOOP:AUX:None"
            ":D:1.0"
            ":HTR:None"
            ":I:1.0"
            ":THTF:None"
            ":HSET:{heater_percent:.4f}"
            ":PIDT:OFF"
            ":ENAB:{heater_auto}"
            ":SWFL:None"
            ":FAUT:OFF"
            ":FSET:0"
            ":PIDF:None"
            ":P:1.0"
            ":SWMD:FIX"
            ":TSET:{tset:.4f}K"
            ":MAN:HVER:1"
            ":FVER:1.12"
            ":SERL:111450078"
            ":CAL:OFFS:0"
            ":COLDL:999.00K"
            ":INT:LIN:SCAL:1"
            ":FILE:None"
            ":HOTL:999.00K"
            ":TYPE:TCE"
            ":SIG:VOLT:-0.0038mV"
            ":CURR:-0.0000A"
            ":TEMP:{temp:.4f}K"
            ":POWR:0.0000W"
            ":RES:0.0000O"
            ":SLOP:0.0000O/K".format(
                name=channel,
                tset=temperature_channel.temperature_sp,
                temp=temperature_channel.temperature,
                heater_auto="ON" if temperature_channel.heater_auto else "OFF",
                heater_percent=temperature_channel.heater_percent,
            )
        )

    @if_connected
    def get_channel_temp(self, chan):
        return "STAT:DEV:{}:TEMP:SIG:TEMP:{:.4f}K".format(
            chan, self.device.temperature_channels[chan.upper()].temperature
        )

    @if_connected
    def get_channel_temp_sp(self, chan):
        return "STAT:DEV:{}:TEMP:LOOP:TSET:{:.4f}K".format(
            chan, self.device.temperature_channels[chan.upper()].temperature_sp
        )

    @if_connected
    def get_channel_heater_auto(self, chan):
        return "STAT:DEV:{}:TEMP:LOOP:ENAB:{}".format(
            chan,
            "ON" if self.device.temperature_channels[chan.upper()].heater_auto else "OFF",
        )

    @if_connected
    def get_channel_heater_percentage(self, chan):
        return "STAT:DEV:{}:TEMP:LOOP:HSET:{:.4f}".format(
            chan, self.device.temperature_channels[chan.upper()].heater_percent
        )

    # Individual channel stabilities

    @if_connected
    def get_he3_sorb_stable(self):
        return "STAT:DEV:{}:HEL:SIG:SRBS:{}".format(
            PRIMARY_DEVICE_NAME,
            "Stable" if self.device.temperature_channels["HE3SORB"].stable else "Unstable",
        )

    @if_connected
    def get_he4_pot_stable(self):
        return "STAT:DEV:{}:HEL:SIG:H4PS:{}".format(
            PRIMARY_DEVICE_NAME,
            "Stable" if self.device.temperature_channels["HE4POT"].stable else "Unstable",
        )
