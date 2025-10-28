import struct
from collections import OrderedDict

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import DefaultState


@has_log
class SimulatedMoxa1210(StateMachineDevice):
    """Simulated Moxa ioLogik E1210 Remote I/O device."""

    def _initialize_data(self):
        """Sets the initial state of the device"""

    def _get_state_handlers(self):
        """Returns: states and their names"""
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """Returns: the name of the initial state"""
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions"""
        return OrderedDict()

    def get_di(self, addr, count):
        """Gets values from a register on the modbus interface

        Args:
            addr: Integer, the starting address of the values to be retrieved
            count: Integer, the number of contiguous values to get from the modbus register

        Returns:
            Array of values with length count

        """
        return self.interface.di.get(addr, count)

    def set_di(self, addr, value):
        """Sets values in the register on the modbus interface

        Args:
            addr: Integer, starting address of the values to be set
            value: List, Containing the data to be written to the register

        Returns:
            None
        """
        self.interface.di.set(addr, value)

    def set_ir(self, addr, value):
        """Set value(s) on the input registers.

        Args:
            addr: Integer, starting address of the values to be set
            value: List, containing the values to be written to the register

        Returns:
            None

        """
        self.interface.ir.set(addr, value)

    def get_ir(self, addr, count):
        """Get value(s) from the input registers.

        Args:
            addr: Integer, starting address of the values to be set
            count: Integer, the number of contiguous values to get from the modbus register

        Returns:
            None

        """
        self.interface.ir.get(addr, count)

    def set_1240_voltage(self, addr, value):
        """Writes to an input register data a voltage encoded like a moxa e1240 voltage/current logger

        The voltage range for an e1240 is a 0 - 10 V. This is linearly encoded in a 16-bit int, so 0=0V and 2**16=10V

        Args:
            addr: Integer, The address to write the value to
            value: Float, The desired voltage to be written to the input register

        Returns:

        """
        max_16_bit_value = 2**16 - 1
        max_voltage_range = 10.0
        min_voltage_range = 0.0

        if value > max_voltage_range:
            raw_val = max_16_bit_value
        elif value < min_voltage_range:
            raw_val = 0
        else:
            raw_val = int(float(value) * max_16_bit_value / max_voltage_range)

        self.interface.ir.set(addr, (raw_val,))

    def set_1262_temperature(self, addr, value):
        """Encodes the requested temperature as two 16-bit integer words and writes to input registers like a moxa e1262

        Follows these stack overflow answers: https://stackoverflow.com/a/35603706, https://stackoverflow.com/a/45354944

        Args:
            addr: The input register to write the first word of the temperature in. The second word will be written to addr+1
            value: Float, the desired temperature to be written to the input registers

        Returns:
            None

        """
        # Convert floating point number to binary representation string
        binary_representation = struct.pack("<f", value)

        # Represent the binary as two unsigned int 'words' (H is unsigned int)
        word1, word2 = struct.unpack("<HH", binary_representation)

        # Write to device
        self.interface.ir.set(addr, (word1, word2))
