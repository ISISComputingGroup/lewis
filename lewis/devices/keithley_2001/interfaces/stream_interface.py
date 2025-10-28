from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


class Keithley2001StreamInterface(StreamInterface):
    in_terminator = "\r\n"
    out_terminator = "\n"

    _channel_readback_format = None

    commands = {
        # Commands used on setup
        CmdBuilder("get_idn").escape("*IDN?").eos().build(),
        CmdBuilder("reset_device").escape("*RST").eos().build(),
        CmdBuilder("set_buffer_source").escape(":DATA:FEED ").arg("NONE|SENS1|CALC1").eos().build(),
        CmdBuilder("get_buffer_source").escape(":DATA:FEED?").eos().build(),
        CmdBuilder("set_buffer_egroup").escape(":DATA:EGR ").arg("FULL|COMP").eos().build(),
        CmdBuilder("get_buffer_egroup").escape(":DATA:EGR?").eos().build(),
        CmdBuilder("set_continuous_initialization")
        .escape(":INIT:CONT ")
        .arg("OFF|ON")
        .eos()
        .build(),
        CmdBuilder("get_continuous_initialization_status").escape(":INIT:CONT?").eos().build(),
        CmdBuilder("get_elements").escape(":FORM:ELEM?").eos().build(),
        CmdBuilder("set_elements").escape(":FORM:ELEM ").string().eos().build(),
        CmdBuilder("get_measurement_status").escape(":STAT:MEAS:ENAB?").eos().build(),
        CmdBuilder("set_buffer_full_status").escape(":STAT:MEAS:ENAB 512").eos().build(),
        CmdBuilder("get_service_request_status").escape("*SRE?").eos().build(),
        CmdBuilder("set_measure_summary_status").escape("*SRE 1").eos().build(),
        CmdBuilder("reset_and_clear_status_registers").escape(":STAT:PRES; *CLS").eos().build(),
        CmdBuilder("set_scan_count").escape(":ARM:LAY2:COUN ").int().eos().build(),
        CmdBuilder("get_scan_count").escape(":ARM:LAY2:COUN?").eos().build(),
        CmdBuilder("get_scan_trigger").escape(":ARM:LAY2:SOUR?").eos().build(),
        # Reading a single channel
        CmdBuilder("set_read_channel").escape(":ROUT:CLOS (@").int().escape(")").eos().build(),
        CmdBuilder("read_single_channel").escape(":READ?").eos().build(),
        # Reading from the buffer
        CmdBuilder("set_buffer_mode")
        .escape(":DATA:FEED:CONT ")
        .arg("NEV|NEXT|ALW|PRET")
        .eos()
        .build(),
        CmdBuilder("get_buffer_mode").escape(":DATA:FEED:CONT?").eos().build(),
        CmdBuilder("clear_buffer").escape(":DATA:CLE").eos().build(),
        CmdBuilder("scan_channels").escape(":INIT").eos().build(),
        CmdBuilder("get_buffer_date").escape(":DATA:DATA?").eos().build(),
        # Setting up a scan
        CmdBuilder("set_measurement_scan_count").escape(":TRIG:COUN ").int().eos().build(),
        CmdBuilder("get_measurement_scan_count").escape(":TRIG:COUN?").eos().build(),
        CmdBuilder("set_buffer_size").escape(":DATA:POIN ").int().eos().build(),
        CmdBuilder("get_buffer_size").escape(":DATA:POIN?").eos().build(),
        CmdBuilder("set_scan_channels")
        .escape(":ROUT:SCAN (@")
        .arg("[0-9,]+")
        .escape(")")
        .eos()
        .build(),
        CmdBuilder("get_scan_channels").escape(":ROUT:SCAN?").eos().build(),
        # Error handling
        CmdBuilder("get_error").escape(":SYST:ERR?").eos().build(),
    }

    def handle_error(self, request, error):
        self.log.error("An error occurred at request {}: {}".format(repr(request), repr(error)))
        print("An error occurred at request {}: {}".format(repr(request), repr(error)))

    # Commands used on setup
    @conditional_reply("_connected")
    def get_idn(self):
        """Returns the devices IDN string.

        Returns:
            string: The device's IDN.
        """
        idn = self._device.idn
        return idn

    @conditional_reply("_connected")
    def get_elements(self):
        """Returns the lists of elements of a reading in alphabetical order from the device.

        """
        elements = [element for element, value in self._device.elements.items() if value]
        return ", ".join(elements)

    @conditional_reply("_connected")
    def set_elements(self, string):
        """Sets the elements a reading has.

        Args:
            string: String of comma separated elements of a reading. Valid elements are:
                READ, CHAN, RNUM, UNIT, TIME, STAT.
        """
        elements = {element.strip().upper() for element in string.split(",")}

        for element in elements:
            try:
                self._device.elements[element] = True
            except LookupError:
                self.log.error(
                    "Tried to set {} which is not a valid reading element.".format(element)
                )
                print("Tried to set {} which is not a valid reading element.".format(element))

        self._generate_readback_format()

    @conditional_reply("_connected")
    def _generate_readback_format(self):
        """Generates the readback format for buffer readings.
        """
        readback_elements = []

        if self._device.elements["READ"]:
            readback_elements.append("{:.7E}")
            if self._device.elements["UNIT"]:
                readback_elements.append("{}")

        if self._device.elements["CHAN"]:
            readback_elements.append(",{:02d}")
            if self._device.elements["UNIT"]:
                readback_elements.append("INTCHAN")

        self._channel_readback_format = "".join(readback_elements)

    @conditional_reply("_connected")
    def reset_device(self):
        """Resets device.
        """
        self._device.reset_device()

    @conditional_reply("_connected")
    def set_buffer_source(self, source):
        """Sets the buffer source.
        """
        self._device.buffer.source = source

    @conditional_reply("_connected")
    def get_buffer_source(self):
        """Gets the buffer source.
        """
        return self._device.buffer.source

    @conditional_reply("_connected")
    def set_buffer_egroup(self, egroup):
        """Sets the buffer element group.
        """
        self._device.number_of_times_ioc_has_been_reset += 1

        self._device.buffer.egroup = egroup

    @conditional_reply("_connected")
    def get_buffer_egroup(self):
        """Gets the buffer element group.
        """
        return self._device.buffer.egroup

    @conditional_reply("_connected")
    def set_continuous_initialization(self, value):
        """Sets continuous scanning status to ON or OFF.

        Thus is called continuous initialization mode in the Keithley 2001 manual.

        Args:
            value (string): ON or OFF.
        """
        if value.upper() == "ON":
            self._device.continuous_initialisation_status = True
        elif value.upper() == "OFF":
            self._device.continuous_initialisation_status = False
        else:
            raise ValueError("Not a valid continuous initialisation mode")

    @conditional_reply("_connected")
    def get_continuous_initialization_status(self):
        """Gets the continuous scanning status.

        Thus is the continuous initialization mode in the Keithley 2001 manual.
        """
        status = "OFF"

        if self._device.continuous_initialisation_status:
            status = "ON"

        return status

    @conditional_reply("_connected")
    def set_buffer_full_status(self):
        """Sets the buffer full status of the status register to true.
        """
        self._device.status_register.buffer_full = True

    @conditional_reply("_connected")
    def set_measure_summary_status(self):
        """Sets the measurement summary status of the status register to true.
        """
        self._device.status_register.measurement_summary_status = True

    @conditional_reply("_connected")
    def get_measurement_status(self):
        """Returns the measurement status of the device.

        Returns:
            string: integer which represents the measurement status register status in bits.
        """
        status = 0
        if self._device.status_register.buffer_full:
            status += 512

        return str(status)

    @conditional_reply("_connected")
    def get_service_request_status(self):
        """Returns the measurement status of the device.

        Returns:
            string: integer which represents the service register status in bits.
        """
        status = 0
        if self._device.status_register.measurement_summary_status:
            status += 1

        return str(status)

    @conditional_reply("_connected")
    def reset_and_clear_status_registers(self):
        """Resets and clears the status registers of the device.
        """
        self._device.status_register.reset_and_clear()

    @conditional_reply("_connected")
    def set_scan_count(self, value):
        """Sets the scan count.

        Args:
            value (int): Number of times to scan.
        """
        self._device.scan_count = int(value)

    @conditional_reply("_connected")
    def get_scan_count(self):
        """Returns the number of times the device is set to scan.

        Returns:
            string: Number of times the device is set to scan.
        """
        return str(self._device.scan_count)

    @conditional_reply("_connected")
    def get_scan_trigger(self):
        """Returns the scan trigger type.

        Returns:
            string: Scan trigger mode. One of IMM, HOLD, MAN, BUS, TLINK, EXT, TIM.
        """
        return self._device.scan_trigger_type

    # Reading a single channel
    @conditional_reply("_connected")
    def set_read_channel(self, channel):
        """Sets the channels to read from in single read mode.

        Args:
            channel string): String representation of a channel number between 1 and 10.
        """
        self._device.close_channel(int(channel))

    @conditional_reply("_connected")
    def read_single_channel(self):
        """Takes a single reading from the closed channel on the device.

        Returns:
            string: Formatted string of channel data.
        """
        channel_data = self._device.take_single_reading()

        return "".join(self._format_buffer_readings(channel_data))

    # Setting up for a scan
    @conditional_reply("_connected")
    def set_buffer_mode(self, mode):
        """Sets the buffer mode.
        """
        self._device.buffer.mode = mode

    @conditional_reply("_connected")
    def get_buffer_mode(self):
        """Gets the buffer mode.
        """
        return self._device.buffer.mode

    @conditional_reply("_connected")
    def set_buffer_size(self, size):
        """Sets the buffer mode.
        """
        self._device.buffer.size = int(size)

    @conditional_reply("_connected")
    def get_buffer_size(self):
        """Gets the buffer mode.
        """
        return self._device.buffer.size

    @conditional_reply("_connected")
    def clear_buffer(self):
        """Clears the buffer.
        """
        self._device.buffer.clear_buffer()

    @conditional_reply("_connected")
    def set_scan_channels(self, channels):
        """Sets the channels to scan.

        Args:
            channels (string): Comma separated list of channel number to read from.
        """
        channels = channels.split(",")
        self._device.buffer.scan_channels = channels

    @conditional_reply("_connected")
    def get_scan_channels(self):
        """Returns the channels set to scan.

        Returns:
            string: comman separated list of channels set to scan
        """
        return "(@" + ",".join(self._device.buffer.scan_channels) + ")"

    @conditional_reply("_connected")
    def set_measurement_scan_count(self, value):
        """Sets the measurement scan count.

        Args:
            value (int): Number of times to trigger measurements.
        """
        self._device.measurement_scan_count = int(value)

    @conditional_reply("_connected")
    def get_measurement_scan_count(self):
        """Gets the measurement scan count.

        Returns:
            value (int): Number of times to trigger measurements
        """
        return str(self._device.measurement_scan_count)

    @conditional_reply("_connected")
    def scan_channels(self):
        """Sets the device to scan.

        """
        self._device.scan_channels()

    @conditional_reply("_connected")
    def get_buffer_date(self):
        """Returns the buffer data.

        Returns:
            list of strings: List of readings from channels.
        """
        return ",".join(map(self._format_buffer_readings, self._device.buffer.buffer))

    def _format_buffer_readings(self, reading):
        """Formats a reading.

        Args:
            reading: dictionary with keys
                "READ", "READ_UNIT", "CHAN"

        Returns:
            string: Buffer reading formatted depending on elements
        """
        formatted_buffer_reading = []

        if self._device.elements["READ"]:
            formatted_buffer_reading.append(reading["READ"])
            if self._device.elements["UNIT"]:
                formatted_buffer_reading.append(reading["READ_UNIT"])

        if self._device.elements["CHAN"]:
            formatted_buffer_reading.append(reading["CHAN"])

        return self._channel_readback_format.format(*formatted_buffer_reading)

    @conditional_reply("_connected")
    def get_error(self):
        """Returns the error code and message.

        Returns:
            (string): Returns the error string formed of
                error code, error message.
        """
        return ",".join(["{}".format(self._device.error[0]), self._device.error[1]])
