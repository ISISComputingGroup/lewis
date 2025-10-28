from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

# Dictionaries for parameter states (strings required to build reply to "all status" command)
OK_NOK = {True: "OK", False: "NOK"}
ON_OFF = {True: "ON", False: "OFF"}
START_STOP = {True: "START", False: "STOP"}
CW_CCW = {True: "CLOCK", False: "ANTICLOCK"}


@has_log
class FZJDDFCHStreamInterface(StreamInterface):
    """Stream interface for the Ethernet port"""

    commands = {
        CmdBuilder("get_magnetic_bearing_status").arg(".{3}").escape("?;MBON?").build(),
        CmdBuilder("get_all_status").arg(".{3}").escape("?;ASTA?").build(),
        CmdBuilder("set_frequency", arg_sep="")
        .arg(".{3}")
        .escape("!;FACT!;")
        .int()
        .build(),
        CmdBuilder("set_phase", arg_sep="")
        .arg(".{3}")
        .escape("!;PHAS!;")
        .float()
        .build(),
        CmdBuilder("set_magnetic_bearing", arg_sep="")
        .arg(".{3}")
        .escape("!;MAGB!;")
        .any()
        .build(),
        CmdBuilder("set_drive_mode", arg_sep="")
        .arg(".{3}")
        .escape("!;DRIV!;")
        .any()
        .build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        """If command is not recognised, print and error

        Args:
            request: requested string
            error: problem
        """
        self.log.error(
            "An error occurred at request " + repr(request) + ": " + repr(error)
        )

    @conditional_reply("connected")
    def set_frequency(self, chopper_name, frequency):
        """Sets the frequency setpoint by multiplying input value by reference frequency

        Args:
            chopper_name: Chopper name (C01, C02, C2B, C03)
            frequency: Frequency setpoint multiple (1, 2, 3, ... 12)

        Returns: OK or error
        """
        if self._device.error_on_set_frequency is None:
            self._device.frequency_setpoint = (
                frequency * self._device.frequency_reference
            )
            reply = "{chopper_name}OK".format(chopper_name=chopper_name)
        else:
            reply = "ERROR;{}".format(self._device.error_on_set_frequency)

        self.log.info(reply)
        return reply

    @conditional_reply("connected")
    def set_phase(self, chopper_name, phase):
        """Sets the phase setpoint

        Args:
            chopper_name:  Chopper name (C01, C02, C2B, C03)
            phase: Phase setpoint (0.01 ... 359.99)

        Returns: OK or error
        """
        if self._device.error_on_set_phase is None:
            self._device.phase_setpoint = phase
            reply = "{chopper_name}OK".format(chopper_name=chopper_name)
        else:
            reply = "ERROR;{}".format(self._device.error_on_set_phase)

        self.log.info(reply)
        return reply

    @conditional_reply("connected")
    def set_magnetic_bearing(self, chopper_name, magnetic_bearing):
        """Sets the state of the magnetic bearings

        Args:
            chopper_name:  Chopper name (C01, C02, C2B, C03)
            magnetic_bearing: boolean value to set magnetic bearings on or off ("ON", "OFF")

        Returns: OK or error
        """
        if self._device.error_on_set_magnetic_bearing is None:
            # Lookup the bool representation of the string
            inverted_on_off_dict = {
                str_val: bool_val for (bool_val, str_val) in ON_OFF.items()
            }
            self._device.magnetic_bearing_is_on = inverted_on_off_dict[magnetic_bearing]
            reply = "{chopper_name}OK".format(chopper_name=chopper_name)
        else:
            reply = "ERROR;{}".format(self._device.error_on_set_magnetic_bearing)

        self.log.info(reply)
        return reply

    @conditional_reply("connected")
    def set_drive_mode(self, chopper_name, drive_mode):
        """Sets the drive mode

        Args:
            chopper_name:   Chopper name (C01, C02, C2B, C03)
            drive_mode: boolean value to set drive ("START", "STOP")

        Returns: OK or error
        """
        if self._device.error_on_set_drive_mode is None:
            # Lookup the bool representation of the string
            inverted_start_stop_dict = {
                str_val: bool_val for (bool_val, str_val) in START_STOP.items()
            }
            self._device.drive_mode_is_start = inverted_start_stop_dict[drive_mode]
            reply = "{chopper_name}OK".format(chopper_name=chopper_name)
        else:
            reply = "ERROR;{}".format(self._device.error_on_set_drive_mode)

        self.log.info(reply)
        return reply

    @conditional_reply("connected")
    def get_magnetic_bearing_status(self, chopper_name):
        """Gets the magnetic bearing status

        Args:
            chopper_name:  Chopper name (e.g. C01, C02, C2B, C03)

        Returns: magnetic bearing status
        """
        device = self._device
        return "{0:3s};MBON?;{}".format(
            device.chopper_name,
        )

    @conditional_reply("connected")
    def get_all_status(self, chopper_name):
        """Gets the status as a single string

        Args:
            chopper_name:  Chopper name (e.g. C01, C02, C2B, C03)

        Returns: string containing values for all parameters
        """
        device = self._device
        if chopper_name != device.chopper_name:
            return None

        values = [
            "{0:3s}".format(device.chopper_name),
            "ASTA?",  # device echoes command
            "{0:3s}".format(device.chopper_name),
            "{0:2d}".format(
                device.frequency_setpoint // device.frequency_reference
            ),  # multiplier of reference frequency
            "{0:.2f}".format(device.frequency_setpoint),
            "{0:.2f}".format(device.frequency),
            "{0:.1f}".format(device.phase_setpoint),
            "{0:.1f}".format(device.phase),
            "{0:s}".format(OK_NOK[device.phase_status_is_ok]),
            "{0:s}".format(ON_OFF[device.magnetic_bearing_is_on]),
            "{0:s}".format(OK_NOK[device.magnetic_bearing_status_is_ok]),
            "{0:s}".format(ON_OFF[device.drive_is_on]),
            "{0:s}".format(START_STOP[device.drive_mode_is_start]),
            "{0:.2f}".format(device.drive_l1_current),
            "{0:.2f}".format(device.drive_l2_current),
            "{0:.2f}".format(device.drive_l3_current),
            "{0:s}".format(CW_CCW[device.drive_direction_is_cw]),
            "{0:.2f}".format(device.drive_temperature),
            "{0:.2f}".format(device.phase_outage),
            "{0:2s}".format(device.master_chopper),
            "{0:s}".format(ON_OFF[device.logging_is_on]),
            "{0:s}".format(
                OK_NOK[False]
            ),  # Device always responds with "NOK" - constant defined in server code
            "{0:s}".format(OK_NOK[device.dsp_status_is_ok]),
            "{0:s}".format(OK_NOK[device.interlock_er_status_is_ok]),
            "{0:s}".format(OK_NOK[device.interlock_vacuum_status_is_ok]),
            "{0:s}".format(OK_NOK[device.interlock_frequency_monitoring_status_is_ok]),
            "{0:s}".format(
                OK_NOK[
                    device.interlock_magnetic_bearing_amplifier_temperature_status_is_ok
                ]
            ),
            "{0:s}".format(
                OK_NOK[device.interlock_magnetic_bearing_amplifier_current_status_is_ok]
            ),
            "{0:s}".format(
                OK_NOK[device.interlock_drive_amplifier_temperature_status_is_ok]
            ),
            "{0:s}".format(
                OK_NOK[device.interlock_drive_amplifier_current_status_is_ok]
            ),
            "{0:s}".format(OK_NOK[device.interlock_ups_status_is_ok]),
        ]

        status_string = ";".join(values)
        return status_string
