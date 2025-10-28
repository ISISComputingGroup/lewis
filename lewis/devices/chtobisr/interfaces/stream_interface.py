from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


@has_log
class ChtobisrStreamInterface(StreamInterface):
    """Stream interface for the Coherent OBIS Laser Remote"""

    commands = {
        CmdBuilder("get_id").escape("*IDN?").build(),
        CmdBuilder("set_reset").escape("*RST").build(),
        CmdBuilder("get_interlock").escape("SYSTEM:LOCK?").build(),
        CmdBuilder("get_status").escape("SYSTEM:STATUS?").build(),
        CmdBuilder("get_faults").escape("SYSTEM:FAULT?").build(),
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
    def get_id(self):
        """Gets the device Identification string

        :return:  Device ID string
        """
        return "{}".format(self._device.id)

    @conditional_reply("connected")
    def set_reset(self):
        """Resets the device

        :return:  none
        """
        self._device.reset()

    @conditional_reply("connected")
    def get_interlock(self):
        """Gets the device interlock status

        :return: Interlock status
        """
        return "{}".format(self._device.interlock)

    @conditional_reply("connected")
    def get_status(self):
        """Returns status code
        :return: Formatted status code
        """
        return "{:08X}".format(self._device.build_status_code())

    @conditional_reply("connected")
    def get_faults(self):
        """Returns faults code
        :return: Formatted fault code
        """
        return "{:08X}".format(self._device.build_fault_code())
