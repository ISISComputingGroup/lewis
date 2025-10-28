from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder


def if_connected(f):
    """Decorator that executes f if the device is connected and returns None otherwise.

    Args:
        f: function to be executed if the device is connected.

    Returns:
        The value of f(*args) if the device is connected and None otherwise.
    """

    def wrapper(*args):
        connected = getattr(args[0], "_device").connected
        if connected:
            result = f(*args)
        else:
            result = None
        return result

    return wrapper


class Lakeshore218StreamInterface(StreamInterface):
    """Stream interface for the serial port"""

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    commands = {
        CmdBuilder("get_temp").escape("KRDG? ").arg("[1-8]").build(),
        CmdBuilder("get_sensor").escape("SRDG? ").arg("[1-8]").build(),
        CmdBuilder("get_temp_all").escape("KRDG? 0").build(),
        CmdBuilder("get_sensor_all").escape("SRDG? 0").build(),
    }

    @if_connected
    def get_temp(self, number):
        """Returns the temperature of a TEMP pv.

        Args:
            number: integer between 1 and 8

        Returns:
            float: temperature
        """
        number = int(number)
        temperature = self._device.get_temp(number)
        return temperature

    @if_connected
    def get_sensor(self, number):
        """Returns the temperature of a SENSOR pv.

        Args:
            number: integer between 1 and 8

        Returns:
            float: sensor_reading
        """
        number = int(number)
        sensor_reading = self._device.get_sensor(number)
        return sensor_reading

    @if_connected
    def get_temp_all(self):
        """Returns a string from TEMPALL pv.

        Returns:
            string: value of TEMPALL pv.
        """
        return self._device.temp_all

    @if_connected
    def get_sensor_all(self):
        """Returns a string from SENSORALL pv.

        Returns:
            string: value of SENSORALL pv.
        """
        return self._device.sensor_all
