from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder

from ..control_modes import OutputMode

SCI_NOTATION_REGEX = r"[-+]?[0-9]*\.?[0-9]*e?[-+]?[0-9]+"


@has_log
class Keithley2400StreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    serial_commands = {
        CmdBuilder("get_values").escape(":READ?").build(),
        CmdBuilder("get_values").escape(":MEAS:VOLT?").build(),
        CmdBuilder("get_values").escape(":MEAS:CURR?").build(),
        CmdBuilder("get_values").escape(":MEAS:RES?").build(),
        CmdBuilder("reset").escape("*RST").build(),
        CmdBuilder("identify").escape("*IDN?").build(),
        CmdBuilder("get_output_mode").escape(":OUTP?").build(),
        CmdBuilder("set_output_mode").escape(":OUTP ").enum("0", "1").build(),
        CmdBuilder("get_offset_compensation_mode").escape(":SENS:RES:OCOM?").build(),
        CmdBuilder("set_offset_compensation_mode").escape(":SENS:RES:OCOM ").enum("0", "1").build(),
        CmdBuilder("get_resistance_mode").escape(":SENS:RES:MODE?").build(),
        CmdBuilder("set_resistance_mode").escape(":SENS:RES:MODE ").enum("AUTO", "MAN").build(),
        CmdBuilder("get_remote_sensing_mode").escape(":SYST:RSEN?").build(),
        CmdBuilder("set_remote_sensing_mode").escape(":SYST:RSEN ").enum("0", "1").build(),
        CmdBuilder("get_resistance_range_mode").escape(":SENS:RES:RANG:AUTO?").build(),
        CmdBuilder("set_resistance_range_mode")
        .escape(":SENS:RES:RANG:AUTO ")
        .enum("0", "1")
        .build(),
        CmdBuilder("get_resistance_range").escape(":SENS:RES:RANG?").build(),
        CmdBuilder("set_resistance_range")
        .escape(":SENS:RES:RANG ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
        CmdBuilder("get_source_mode").escape(":SOUR:FUNC?").build(),
        CmdBuilder("set_source_mode").escape(":SOUR:FUNC ").enum("CURR", "VOLT").build(),
        CmdBuilder("get_current_compliance").escape(":SENS:CURR:PROT?").build(),
        CmdBuilder("set_current_compliance")
        .escape(":SENS:CURR:PROT ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
        CmdBuilder("get_voltage_compliance").escape(":SENS:VOLT:PROT?").build(),
        CmdBuilder("set_voltage_compliance")
        .escape(":SENS:VOLT:PROT ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
        CmdBuilder("get_source_voltage").escape(":SOUR:VOLT:LEV?").build(),
        CmdBuilder("set_source_voltage").escape(":SOUR:VOLT:LEV ").arg(SCI_NOTATION_REGEX).build(),
        CmdBuilder("get_source_current").escape(":SOUR:CURR:LEV?").build(),
        CmdBuilder("set_source_current").escape(":SOUR:CURR:LEV ").arg(SCI_NOTATION_REGEX).build(),
        CmdBuilder("get_source_current_autorange_mode").escape(":SOUR:CURR:RANG:AUTO?").build(),
        CmdBuilder("set_source_current_autorange_mode")
        .escape(":SOUR:CURR:RANG:AUTO ")
        .enum("0", "1")
        .build(),
        CmdBuilder("get_source_voltage_autorange_mode").escape(":SOUR:VOLT:RANG:AUTO?").build(),
        CmdBuilder("set_source_voltage_autorange_mode")
        .escape(":SOUR:VOLT:RANG:AUTO ")
        .enum("0", "1")
        .build(),
        CmdBuilder("get_source_current_range").escape(":SOUR:CURR:RANG?").build(),
        CmdBuilder("set_source_current_range")
        .escape(":SOUR:CURR:RANG ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
        CmdBuilder("get_source_voltage_range").escape(":SOUR:VOLT:RANG?").build(),
        CmdBuilder("set_source_voltage_range")
        .escape(":SOUR:VOLT:RANG ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
        CmdBuilder("get_measured_voltage_autorange_mode").escape(":SENS:VOLT:RANG:AUTO?").build(),
        CmdBuilder("set_measured_voltage_autorange_mode")
        .escape(":SENS:VOLT:RANG:AUTO ")
        .enum("0", "1")
        .build(),
        CmdBuilder("get_measured_current_autorange_mode").escape(":SENS:CURR:RANG:AUTO?").build(),
        CmdBuilder("set_measured_current_autorange_mode")
        .escape(":SENS:CURR:RANG:AUTO ")
        .enum("0", "1")
        .build(),
        CmdBuilder("get_measured_current_range").escape(":SENS:CURR:RANG?").build(),
        CmdBuilder("set_measured_current_range")
        .escape(":SENS:CURR:RANG ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
        CmdBuilder("get_measured_voltage_range").escape(":SENS:VOLT:RANG?").build(),
        CmdBuilder("set_measured_voltage_range")
        .escape(":SENS:VOLT:RANG ")
        .arg(SCI_NOTATION_REGEX)
        .build(),
    }

    # Private control commands that can be used as an alternative to the lewis backdoor
    control_commands = {
        Cmd("set_voltage", "^\:_CTRL:VOLT\s([-+]?[0-9]*\.?[0-9]+)$"),
        Cmd("set_current", "^\:_CTRL:CURR\s([-+]?[0-9]*\.?[0-9]+)$"),
    }

    commands = set.union(serial_commands, control_commands)

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def get_values(self):
        """Get the current, voltage and resistance readings

        :return: A string of 3 doubles: voltage, current, resistance. In that order
        """
        return (
            ", ".join(
                [
                    self._device.get_voltage(as_string=True),
                    self._device.get_current(as_string=True),
                    self._device.get_resistance(as_string=True),
                ]
            )
            if self._device.get_output_mode() == OutputMode.ON
            else None
        )

    def reset(self):
        """Resets the device."""
        self._device.reset()
        return "*RST"

    def identify(self):
        """Replies with the device's identity."""
        return "Keithley 2400 Source Meter emulator"

    def set_current(self, value):
        self._device.set_current(float(value))
        return "Current set to: " + str(value)

    def set_voltage(self, value):
        self._device.set_voltage(float(value))
        return "Voltage set to: " + str(value)

    def _set_mode(self, set_method, mode, command):
        """The generic form of how mode sets are executed and responded to."""
        set_method(mode)

        return command + " " + mode

    def set_output_mode(self, new_mode):
        return self._set_mode(self._device.set_output_mode, new_mode, "OUTP:")

    def get_output_mode(self):
        return self._device.get_output_mode()

    def set_offset_compensation_mode(self, new_mode):
        return self._set_mode(self._device.set_offset_compensation_mode, new_mode, ":SENS:RES:OCOM")

    def get_offset_compensation_mode(self):
        return self._device.get_offset_compensation_mode()

    def set_resistance_mode(self, new_mode):
        return self._set_mode(self._device.set_resistance_mode, new_mode, ":SENS:RES:MODE")

    def get_resistance_mode(self):
        return self._device.get_resistance_mode()

    def set_remote_sensing_mode(self, new_mode):
        return self._set_mode(self._device.set_remote_sensing_mode, new_mode, ":SYST:RSEN")

    def get_remote_sensing_mode(self):
        return self._device.get_remote_sensing_mode()

    def set_resistance_range_mode(self, new_mode):
        return self._set_mode(
            self._device.set_resistance_range_mode, new_mode, ":SENS:RES:RANG:AUTO"
        )

    def get_resistance_range_mode(self):
        return self._device.get_resistance_range_mode()

    def set_resistance_range(self, value):
        return self._device.set_resistance_range(float(value))

    def get_resistance_range(self):
        return self._device.get_resistance_range()

    def set_source_mode(self, new_mode):
        return self._set_mode(self._device.set_source_mode, new_mode, ":SOUR:FUNC")

    def get_source_mode(self):
        return self._device.get_source_mode()

    def set_current_compliance(self, value):
        return self._device.set_current_compliance(float(value))

    def get_current_compliance(self):
        return self._device.get_current_compliance()

    def set_voltage_compliance(self, value):
        return self._device.set_voltage_compliance(float(value))

    def get_voltage_compliance(self):
        return self._device.get_voltage_compliance()

    def set_source_voltage(self, value):
        return self._device.set_source_voltage(float(value))

    def get_source_voltage(self):
        return self._device.get_source_voltage()

    def set_source_current(self, value):
        return self._device.set_source_current(float(value))

    def get_source_current(self):
        return self._device.get_source_current()

    def get_source_current_autorange_mode(self):
        return self._device.get_source_current_autorange_mode()

    def set_source_current_autorange_mode(self, value):
        return self._device.set_source_current_autorange_mode(value)

    def get_source_voltage_autorange_mode(self):
        return self._device.get_source_voltage_autorange_mode()

    def set_source_voltage_autorange_mode(self, value):
        return self._device.set_source_voltage_autorange_mode(value)

    @has_log
    def handle_error(self, request, error):
        err = "An error occurred at request {}: {}".format(str(request), str(error))
        print(err)
        self.log.info(err)
        return str(err)

    def set_source_current_range(self, value):
        return self._device.set_source_current_range(float(value))

    def get_source_current_range(self):
        return self._device.get_source_current_range()

    def set_source_voltage_range(self, value):
        return self._device.set_source_voltage_range(float(value))

    def get_source_voltage_range(self):
        return self._device.get_source_voltage_range()

    def get_measured_voltage_autorange_mode(self):
        return self._device.get_measured_voltage_autorange_mode()

    def set_measured_voltage_autorange_mode(self, value):
        return self._device.set_measured_voltage_autorange_mode(value)

    def get_measured_current_autorange_mode(self):
        return self._device.get_measured_current_autorange_mode()

    def set_measured_current_autorange_mode(self, value):
        val = self._device.set_measured_current_autorange_mode(value)
        return val
