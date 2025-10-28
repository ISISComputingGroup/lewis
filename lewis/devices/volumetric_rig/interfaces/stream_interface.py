from lewis.adapters.stream import Cmd, StreamInterface

from ..sensor_status import SensorStatus
from ..utilities import convert_raw_to_bool, convert_raw_to_float, convert_raw_to_int, format_int
from ..valve_status import ValveStatus


class VolumetricRigStreamInterface(StreamInterface):
    # The rig typically splits a command by whitespace and then uses the arguments it needs and then ignores the rest
    # so "IDN" will respond as "IDN BLAH BLAH BLAH" and "BCS 01" would be the same as "BCS 01 02 03".
    # Some commands that take input will respond with default (often invalid) parameters if not present. For example
    # "BCS" is the same as "BCS 00" and also "BCS AA".
    serial_commands = {
        Cmd("purge", "^(.*)\!$"),
        Cmd("get_identity", "^IDN(?:\s.*)?$"),
        Cmd("get_identity", "^\?(?:\s.*)?$"),
        Cmd("get_buffer_control_and_status", "^BCS(?:\s(\S*))?.*$"),
        Cmd("get_ethernet_and_hmi_status", "^ETN(?:\s.*)?$"),
        Cmd("get_gas_control_and_status", "^GCS(?:\s.*)?$"),
        Cmd("get_gas_mix_matrix", "^GMM(?:\s.*)?$"),
        Cmd("gas_mix_check", "^GMC(?:\s(\S*))?(?:\s(\S*))?.*$"),
        Cmd("get_gas_number_available", "^GNA(?:\s.*)?$"),
        Cmd("get_hmi_status", "^HMI(?:\s.*)?$"),
        Cmd("get_hmi_count_cycles", "^HMC(?:\s.*)?$"),
        Cmd("get_memory_location", "^RDM(?:\s(\S*))?.*"),
        Cmd("get_pressure_and_temperature_status", "^PTS(?:\s.*)?$"),
        Cmd("get_pressures", "^PMV(?:\s.*)?$"),
        Cmd("get_temperatures", "^TMV(?:\s.*)?$"),
        Cmd("get_ports_and_relays_hex", "^PTR(?:\s.*)?$"),
        Cmd("get_ports_output", "^POT(?:\s.*)?$"),
        Cmd("get_ports_input", "^PIN(?:\s.*)?$"),
        Cmd("get_ports_relays", "^PRY(?:\s.*)?$"),
        Cmd("get_system_status", "^STS(?:\s.*)?$"),
        Cmd("get_com_activity", "^COM(?:\s.*)?$"),
        Cmd("get_valve_status", "^VST(?:\s.*)?$"),
        Cmd("open_valve", "^OPV(?:\s(\S*))?.*$"),
        Cmd("close_valve", "^CLV(?:\s(\S*))?.*$"),
        Cmd("halt", "^HLT(?:\s.*)?$"),
    }

    # These commands are intended solely as a control mechanism for the emulator. As an alternative, the Lewis
    # backdoor can be used to modify the device state.
    control_commands = {
        Cmd("set_buffer_system_gas", "^_SBG(?:\s(\S*))?(?:\s(\S*))?.*$"),
        Cmd("set_pressure_cycling", "^_PCY(?:\s(\S*)).*$"),
        Cmd("set_pressures", "^_SPR(?:\s(\S*)).*$"),
        Cmd("set_pressure_target", "^_SPT(?:\s(\S*)).*$"),
        Cmd("enable_valve", "^_ENV(?:\s(\S*)).*$"),
        Cmd("disable_valve", "^_DIV(?:\s(\S*)).*$"),
    }

    commands = set.union(serial_commands, control_commands)

    # You may need to change these to \r\n if using Telnet"
    in_terminator = "\r"
    out_terminator = "\r"

    # Lots of formatted output for the volumetric rig is based on fixed length strings
    output_length = 20

    def purge(self, chars):
        """Responds any current input to the screen without executing it.

        :param chars: Whatever characters are left over in the buffer
        :return: Purge message including ignored input
        """
        return " ".join(
            ["PRG,00,Purge", format_int(len(chars) + 1, True, 5), "Characters", chars + "!"]
        )

    def get_identity(self):
        """Responds with the devices identity.

        :return: Device identity
        """
        return "IDN,00," + self._device.identify()

    def _build_buffer_control_and_status_string(self, buffer_number):
        """Get information about a specific buffer, its valve state and the gases connected to it.

        :param buffer_number : The index of the buffer
        :return: Information about the requested buffer
        """
        buff = self._device.buffer(buffer_number)
        assert buff is not None
        return " ".join(
            [
                "",
                buff.index(as_string=True),
                buff.buffer_gas().index(as_string=True),
                buff.buffer_gas().name(VolumetricRigStreamInterface.output_length, " "),
                "E" if buff.valve_is_enabled() else "d",
                "O" if buff.valve_is_open() else "c",
                buff.system_gas().index(as_string=True),
                buff.system_gas().name(),
            ]
        )

    def get_buffer_control_and_status(self, buffer_number_raw):
        """Get information about a specific buffer, its valve state and the gases connected to it.

        :param buffer_number_raw : The buffer "number" entered by a user. Although a number is expected, the command
            will accept other types of input
        :return: Information about the requested buffer
        """
        buffer_number = convert_raw_to_int(buffer_number_raw)
        message_prefix = "BCS"
        num_length = 3
        error_message_prefix = " ".join(
            [message_prefix, "Buffer", str(buffer_number)[:num_length].zfill(num_length)]
        )
        buffer_too_low = " ".join([error_message_prefix, "Too Low"])
        buffer_too_high = " ".join([error_message_prefix, "Too High"])

        if buffer_number <= 0:
            return buffer_too_low
        elif buffer_number > len(self._device.buffers()):
            return buffer_too_high
        else:
            return "BCS " + self._build_buffer_control_and_status_string(buffer_number)

    def get_ethernet_and_hmi_status(self):
        """Get information about the rig's hmi and plc ethernet devices.

        :return: Information about the ethernet devices status. The syntax of the return string is odd: the
             separators are not consistent
        """
        return " ".join(
            [
                "ETN:PLC",
                self._device.plc().ip() + ",HMI",
                self._device.hmi().status(),
                "," + self._device.hmi().ip(),
            ]
        )

    def get_gas_control_and_status(self):
        """Get a list of information about all the buffers, their associated gases and valve statuses.

        :return: Buffer information. One line per buffer with a header
        """
        return "\r\n".join(
            ["No No Buffer               E O No System"]
            + [
                self._build_buffer_control_and_status_string(b.index())
                for b in self._device.buffers()
            ]
            + ["GCS"]
        )

    def get_gas_mix_matrix(self):
        """Get information about which gases can be mixed together.

        :return: A 2D matrix representation of the ability to mix different gases with column and row titles
        """
        system_gases = self._device.system_gases().gases()
        column_headers = [
            gas.name(VolumetricRigStreamInterface.output_length, "|") for gas in system_gases
        ]
        row_titles = [
            " ".join(
                [
                    gas.index(as_string=True),
                    gas.name(VolumetricRigStreamInterface.output_length, " "),
                ]
            )
            for gas in system_gases
        ]
        mixable_chars = [
            ["<" if self._device.mixer().can_mix(g1, g2) else "." for g1 in system_gases]
            for g2 in system_gases
        ]

        # Put data in output format
        lines = list()
        # Add column headers
        for i in range(len(max(column_headers, key=len))):
            words = list()
            # For the top-left block of white space
            words.append((len(max(row_titles, key=len)) - 1) * " ")
            # Vertically aligned gas names
            for j in range(len(column_headers)):
                words.append(column_headers[j][i])
            lines.append(" ".join(words))
        # Add rows
        assert len(row_titles) == len(mixable_chars)
        for i in range(len(row_titles)):
            words = list()
            words.append(row_titles[i])
            words.append(" ".join(mixable_chars[i]))
            lines.append("".join(words))
        # Add footer
        lines.append("GMM allowance limit: " + str(self._device.system_gases().gas_count()))

        return "\r\n".join(lines)

    def gas_mix_check(self, gas1_index_raw, gas2_index_raw):
        """Query whether two gases can be mixed.

        :param gas1_index_raw : The index of the first gas. Although a number is expected, the command will
             accept other types of input
        :param gas2_index_raw : As above for the 2nd gas

        :return: An echo of the name and index of the requested gases as well as an ok/NO indicating whether the
             gases can be mixed
        """
        gas1 = self._device.system_gases().gas_by_index(convert_raw_to_int(gas1_index_raw))
        gas2 = self._device.system_gases().gas_by_index(convert_raw_to_int(gas2_index_raw))
        if gas1 is None:
            gas1 = self._device.system_gases().gas_by_index(0)
        if gas2 is None:
            gas2 = self._device.system_gases().gas_by_index(0)

        return " ".join(
            [
                "GMC",
                gas1.index(as_string=True),
                gas1.name(VolumetricRigStreamInterface.output_length, "."),
                gas2.index(as_string=True),
                gas2.name(VolumetricRigStreamInterface.output_length, "."),
                "ok" if self._device.mixer().can_mix(gas1, gas2) else "NO",
            ]
        )

    def get_gas_number_available(self):
        """Get the number of available gases.

        :return: The number of available gases
        """
        return self._device.system_gases().gas_count()

    def get_hmi_status(self):
        """Get the current status of the HMI.

        :return: Information about the HMI
        """
        hmi = self._device.hmi()
        return ",".join(
            [
                "HMI " + hmi.status() + " ",
                hmi.ip(),
                "B",
                hmi.base_page(as_string=True, length=3),
                "S",
                hmi.sub_page(as_string=True, length=3),
                "C",
                hmi.count(as_string=True, length=4),
                "L",
                hmi.limit(as_string=True, length=4),
                "M",
                hmi.max_grabbed(as_string=True, length=4),
            ]
        )

    def get_hmi_count_cycles(self):
        """Get information about how frequently the HMI is disconnected.

        :return: A list of integers indicating the number of occurrences of a disconnected count cycle of a specific
             length
        """
        return " ".join(["HMC"] + self._device.hmi().count_cycles())

    def get_memory_location(self, location_raw):
        """Get the value stored in a particular location in memory.

        :param location_raw : The memory location to read. Although a number is expected, the command will accept other
             types of input

        :return: The memory location and the value stored there
        """
        location = convert_raw_to_int(location_raw)
        return " ".join(
            [
                "RDM",
                format_int(location, as_string=True, length=4),
                self._device.memory_location(location, as_string=True, length=6),
            ]
        )

    def get_pressure_and_temperature_status(self):
        """Get the status of the temperature and pressure sensors.

        :return: A letter for each sensor indicating its status. Refer to the spec for the meaning and sensor order
        """
        status_codes = {
            SensorStatus.DISABLED: "D",
            SensorStatus.NO_REPLY: "X",
            SensorStatus.VALUE_IN_RANGE: "O",
            SensorStatus.VALUE_TOO_LOW: "L",
            SensorStatus.VALUE_TOO_HIGH: "H",
            SensorStatus.UNKNOWN: "?",
        }

        return "PTS " + "".join(
            [
                status_codes[s.status()]
                for s in self._device.pressure_sensors(reverse=True)
                + self._device.temperature_sensors(reverse=True)
            ]
        )

    def get_pressures(self):
        """Get the current pressure sensor readings, and target pressure.

        :return: The pressure readings from each of the pressure sensors and the target pressure which, if exceeded,
             will cause all buffer valves to close and disable
        """
        return " ".join(
            ["PMV"]
            + [p.value(as_string=True) for p in self._device.pressure_sensors(reverse=True)]
            + ["T", self._device.target_pressure(as_string=True)]
        )

    def get_temperatures(self):
        """Get the current temperature reading.

        :return: The current temperature for each of the temperature sensors
        """
        return " ".join(
            ["TMV"]
            + [t.value(as_string=True) for t in self._device.temperature_sensors(reverse=True)]
        )

    def get_valve_status(self):
        """Get the status of the buffer and system valves.

        :return: The status of each of the system valves represented by a letter. Refer to the specification for the
            exact meaning and order
        """
        status_codes = {
            ValveStatus.OPEN_AND_ENABLED: "O",
            ValveStatus.CLOSED_AND_ENABLED: "E",
            ValveStatus.CLOSED_AND_DISABLED: "D",
            ValveStatus.OPEN_AND_DISABLED: "!",
        }
        return "VST Valve Status " + "".join(
            [status_codes[v] for v in self._device.valves_status()]
        )

    @staticmethod
    def _convert_raw_valve_to_int(raw):
        """Get the valve number from its identifier.

        :param raw: The raw valve identifier
        :return: An integer indicating the valve number
        """
        if str(raw).lower() == "c":
            n = 7
        elif str(raw).lower() == "v":
            n = 8
        else:
            n = convert_raw_to_int(raw)
        return n

    def _set_valve_status(self, valve_identifier_raw, set_to_open=None, set_to_enabled=None):
        """Change the valve status.

        :param valve_identifier_raw: A raw value that identifies the valve
        :param set_to_open: Whether to set the valve to open(True)/closed(False)/do noting(None)
        :param set_to_enabled: Whether to set the valve to enabled(True)/disabled(False)/do noting(None)
        :return: Indicates the valve number, previous state, and new state
        """
        valve_number = VolumetricRigStreamInterface._convert_raw_valve_to_int(valve_identifier_raw)

        # We should have exactly one of these arguments
        if set_to_open is not None:
            command = "OPV" if set_to_open else "CLV"
        elif set_to_enabled is not None:
            command = "_ENV" if set_to_enabled else "_DIV"
        else:
            assert False

        # The command and valve number are always included
        message_prefix = " ".join([command, "Value", str(valve_number)])

        # Select an action based on the input parameters.
        args = list()
        enabled = lambda *args: None
        if self._device.halted():
            return command + " Rejected only allowed when running"
        elif valve_number <= 0:
            return message_prefix + " Too Low"
        elif valve_number <= self._device.buffer_count():
            if set_to_open is not None:
                action = (
                    self._device.open_buffer_valve
                    if set_to_open
                    else self._device.close_buffer_valve
                )
                enabled = self._device.buffer_valve_is_enabled
                current_state = self._device.buffer_valve_is_open
            else:
                action = (
                    self._device.enable_buffer_valve
                    if set_to_enabled
                    else self._device.disable_buffer_valve
                )
                current_state = self._device.buffer_valve_is_enabled
            args.append(valve_number)
        elif valve_number == self._device.buffer_count() + 1:
            if set_to_open is not None:
                action = (
                    self._device.open_cell_valve if set_to_open else self._device.close_cell_valve
                )
                enabled = self._device.cell_valve_is_enabled
                current_state = self._device.cell_valve_is_open
            else:
                action = (
                    self._device.enable_cell_valve
                    if set_to_enabled
                    else self._device.disable_cell_valve
                )
                current_state = self._device.cell_valve_is_enabled
        elif valve_number == self._device.buffer_count() + 2:
            if set_to_open is not None:
                action = (
                    self._device.open_vacuum_valve
                    if set_to_open
                    else self._device.close_vacuum_valve
                )
                enabled = self._device.vacuum_valve_is_enabled
                current_state = self._device.vacuum_valve_is_open
            else:
                action = (
                    self._device.enable_vacuum_valve
                    if set_to_enabled
                    else self._device.disable_vacuum_valve
                )
                current_state = self._device.vacuum_valve_is_enabled
        else:
            return message_prefix + " Too High"

        if set_to_open is not None:
            if not enabled(*args):
                return " ".join(
                    [command, "Rejected not enabled", format_int(valve_number, True, 1)]
                )
            status_codes = {True: "open", False: "closed"}
        else:
            status_codes = {True: "enabled", False: "disabled"}

        # Execute the action and get the status before and after
        original_status = current_state(*args)
        action(*args)
        new_status = current_state(*args)
        return " ".join(
            [
                command,
                "Valve Buffer",
                str(valve_number),
                status_codes[new_status],
                "was",
                status_codes[original_status],
            ]
        )

    def close_valve(self, valve_number_raw):
        """Close a valve.

        :param valve_number_raw: The number of the valve to close. The first n valves correspond to the buffers where n
             is the number of buffers. The n+1th valve is the cell valve, the n+2nd valve is for the vacuum. The supply
             valve cannot be controlled via serial. Although a number is expected, the command will accept other types
             of input
        :return: Indicates the valve number, previous state, and new state
        """
        return self._set_valve_status(valve_number_raw, set_to_open=False)

    def open_valve(self, valve_number_raw):
        """Open a valve.

        :param valve_number_raw : The number of the valve to close. The first n valves correspond to the buffers where n
             is the number of buffers. The n+1th valve is the cell valve, the n+2nd valve is for the vacuum. The supply
             valve cannot be controlled via serial. Although a number is expected, the command will accept other types
             of input
        :return: Indicates the valve number, previous state, and new state
        """
        return self._set_valve_status(valve_number_raw, set_to_open=True)

    def enable_valve(self, valve_number_raw):
        """Enable a valve.

        :param valve_number_raw: The number of the valve to close. The first n valves correspond to the buffers where n
             is the number of buffers. The n+1th valve is the cell valve, the n+2nd valve is for the vacuum. The supply
             valve cannot be controlled via serial. Although a number is expected, the command will accept other types
             of input
        :return: Indicates the valve number, previous state, and new state
        """
        return self._set_valve_status(convert_raw_to_int(valve_number_raw), set_to_enabled=True)

    def disable_valve(self, valve_number_raw):
        """Disable a valve.

        :param valve_number_raw: The number of the valve to close. The first n valves correspond to the buffers where n
             is the number of buffers. The n+1th valve is the cell valve, the n+2nd valve is for the vacuum. The supply
             valve cannot be controlled via serial. Although a number is expected, the command will accept other types
             of input
        :return: Indicates the valve number, previous state, and new state
        """
        return self._set_valve_status(convert_raw_to_int(valve_number_raw), set_to_enabled=False)

    def halt(self):
        """Halts the device. No further valve commands will be accepted.

        :return: Indicates that the system has been, or was already halted
        """
        if self._device.halted():
            message = "SYSTEM ALREADY HALTED"
        else:
            self._device.halt()
            assert self._device.halted()
            message = "SYSTEM NOW HALTED"
        return "HLT *** " + message + " ***"

    def get_system_status(self):
        """Get information about the current system state.

        :return: Information about the system. Capitalisation of a particular word indicates an error has occurred
             in that subsystem. Refer to the specification for the meaning of system codes
        """
        return " ".join(
            [
                "STS",
                self._device.status_code(as_string=True, length=2),
                "STOP" if self._device.errors().run else "run",
                "HMI" if self._device.errors().hmi else "hmi",
                # Spelling error duplicated as on device
                "GUAGES" if self._device.errors().gauges else "guages",
                "COMMS" if self._device.errors().comms else "comms",
                "HLT" if self._device.halted() else "halted",
                "E-STOP" if self._device.errors().estop else "estop",
            ]
        )

    def get_ports_and_relays_hex(self):
        """:return: Information about the ports and relays"""
        return "PTR I:00 0000 0000 R:0000 0200 0000 O:00 0000 4400"

    def get_ports_output(self):
        """:return: Information about the port output"""
        return "POT qwertyus vsbbbbbbzyxwvuts aBhecSssvsbbbbbb"

    def get_ports_input(self):
        """:return: Information about the port input"""
        return "PIN qwertyui zyxwvutsrqponmlk abcdefghijklmneb"

    def get_ports_relays(self):
        """:return: Information about the port relays."""
        return "PRY qwertyuiopasdfgh zyxwhmLsrqponmlk abcdefghihlbhace"

    def get_com_activity(self):
        """:return: Information about activity over the COM port"""
        return "COM ok  0113/0000"

    def set_buffer_system_gas(self, buffer_index_raw, gas_index_raw):
        """Changes the system gas associated with a particular buffer.

        :param buffer_index_raw: The index of the buffer to update
        :param gas_index_raw: The index of the gas to update
        :return: Indicates the buffer changed, the previous system gas and the new system gas
        """
        gas = self._device.system_gases().gas_by_index(convert_raw_to_int(gas_index_raw))
        buff = self._device.buffer(convert_raw_to_int(buffer_index_raw))
        if gas is not None and buff is not None:
            original_gas = buff.system_gas()
            buff.set_system_gas(gas)
            new_gas = buff.system_gas()
            return " ".join(
                [
                    "SBG Buffer",
                    buff.index(as_string=True),
                    "system gas was",
                    original_gas.name(),
                    "now",
                    new_gas.name(),
                ]
            )
        else:
            return "SBG Lookup failed"

    def set_pressure_cycling(self, on_int_raw):
        """Starts a sequence of pressure cycling. The pressure is increased until the target is met. This disables all
        buffer valves. The system pressure is decreased and the valves are renabled and reopened when the pressure
        falls below set limits. When the pressure reaches a minimum, the cycle is restarted. This allows simulation
        of various valve conditions.

        :param on_int_raw: Whether to switch cycling on(1)/off(other)
        :return: Indicates whether cycling is enabled
        """
        cycle = convert_raw_to_bool(on_int_raw)
        self._device.cycle_pressures(cycle)
        return "_PCY " + str(cycle)

    def set_pressures(self, value_raw):
        """Set the reading for all pressure sensors to a fixed value.

        :param value_raw: The value to apply to the pressure sensors
        :return: Echo the new pressure
        """
        value = convert_raw_to_float(value_raw)
        self._device.set_pressures(value)
        return "SPR Pressures set to " + str(value)

    def set_pressure_target(self, value_raw):
        """Set the target (limit) pressure for the system.

        :param value_raw: The new pressure target
        :return: Echo the new target
        """
        value = convert_raw_to_float(value_raw)
        self._device.set_pressure_target(value)
        return "SPT Pressure target set to " + str(value)

    def handle_error(self, request, error):
        """Handle errors during execution. May be an unrecognised command or emulator failure."""
        if str(error) == "None of the device's commands matched.":
            return "URC,04,Unrecognised Command," + str(request)
        else:
            print("An error occurred at request " + repr(request) + ": " + repr(error))
