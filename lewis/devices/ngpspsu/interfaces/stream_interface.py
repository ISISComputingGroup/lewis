from lewis.devices.ngpspsu.interfaces.device_status import DeviceStatus

from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


class NgpspsuStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("get_version").escape("VER").eos().build(),
        CmdBuilder("start").escape("MON").eos().build(),
        CmdBuilder("stop").escape("MOFF").eos().build(),
        CmdBuilder("read_status").escape("MST").eos().build(),
        CmdBuilder("reset").escape("MRESET").eos().build(),
        CmdBuilder("read_voltage").escape("MRV").build(),
        CmdBuilder("set_voltage_setpoint").escape("MWV:").float().eos().build(),
        CmdBuilder("read_voltage_setpoint").escape("MWV:?").eos().build(),
        CmdBuilder("read_current").escape("MRI").eos().build(),
        CmdBuilder("set_current_setpoint").escape("MWI:").float().eos().build(),
        CmdBuilder("read_current_setpoint").escape("MWI:?").eos().build(),
    }

    out_terminator = "\r\n"
    in_terminator = "\r"

    def handle_error(self, request, error):
        """Prints an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            None.
        """
        self.log.error(
            "An error occurred at request " + repr(request) + ": " + repr(error)
        )

        print("An error occurred at request {}: {}".format(request, error))

    @if_connected
    def get_version(self):
        """Returns the model number and firmware of the device

        E.g. "#VER:NGPS 100-50:0.9.01" where "NGPS 100-50" is the model
            number and "0.9.01" is the firmware number.
        """
        return "#VER:{}".format(self._device.model_number_and_firmware)

    @if_connected
    def start(self):
        """Starts the device.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code.).
        """
        return self._device.start_device()

    @if_connected
    def stop(self):
        """Stops the device.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code.).
        """
        return self._device.stop_device()

    @if_connected
    def read_status(self):
        """Reads the status of the device.

        Returns:
            string: The status of the device as a string of 8 hexadecimal digits.
        """
        device_status = DeviceStatus(self._device.status)
        hexadecimal_status = device_status.in_hexadecimal()
        return "#MST:{}".format(hexadecimal_status)

    @if_connected
    def reset(self):
        """Resets the device.

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code.).
        """
        return self._device.reset_device()

    @if_connected
    def read_voltage(self):
        """Reads the voltage.

        Returns:
            string: "#MRV:%f" where %f is the voltage of the device to 6 decimal places.
        """
        return "#MRV:{}".format(self._device.voltage)

    @if_connected
    def set_voltage_setpoint(self, value):
        """Sets the voltage setpoint.

        Args:
            value: string of a decimal to 6 decimal places

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code.).
        """
        return self._device.try_setting_voltage_setpoint(value)

    @if_connected
    def read_voltage_setpoint(self):
        """Reads the voltage setpoint.

        Returns:
            string: #MWV:%f" where %f is the voltage setpoint value.
        """
        return "#MWV:{}".format(self._device.voltage_setpoint)

    @if_connected
    def read_current(self):
        """Reads the current.

        Returns:
            string: "#MRI:%f" where %f is the current of the device to 6 decimal places.
        """
        return "#MRI:{}".format(self._device.current)

    @if_connected
    def set_current_setpoint(self, value):
        """Sets the current setpoint.

        Args:
            value: string of a decimal to 6 decimal places

        Returns:
            string: "#AK" if successful, #NK:%i if not (%i is an error code.).
        """
        return self._device.try_setting_current_setpoint(value)

    @if_connected
    def read_current_setpoint(self):
        """Reads the current setpoint.

        Returns:
            string: #MWV:%f" where %f is the current setpoint value.
        """
        return "#MWI:{}".format(self._device.current_setpoint)
