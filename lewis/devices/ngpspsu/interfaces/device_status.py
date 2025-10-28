# Class and function to help convert status into 8 hexadecimal characters

NUMBER_OF_BITS = 32
NUMBER_OF_HEXADECIMAL_CHARACTERS = 8


class DeviceStatus(object):
    """Converts the device's status to a list of 8 hexadecimal characters."""

    _REFERENCE = {
        "0": "ON/OFF",
        "1": "Fault condition",
        "2": "Control mode",
        "5": "Regulation mode",
        "6": "Update mode",
        "12": "Ramping",
        "13": "Waveform",
        "20": "OVT",
        "21": "Mains fault",
        "22": "Earth leakage",
        "23": "Earth fuse",
        "24": "Regulation fault",
        "26": "Ext. interlock #1",
        "27": "Ext. interlock #2",
        "28": "Ext. interlock #3",
        "29": "Ext. interlock #4",
        "30": "DCCT fault",
        "31": "OVP",
    }

    _CONTROL_MODE = {"Remote": [False, False], "Local": [False, True]}

    _UPDATE_MODE = {
        "Normal": [False, False],
        "Waveform": [False, True],
        "Triggered FIFO": [True, False],
        "Analog Input": [True, True],
    }

    def __init__(self, status):
        self._status = status
        self._bits = [False for _ in range(0, NUMBER_OF_BITS)]

    def in_hexadecimal(self):
        """Returns the status of the device as a string of hexadecimal values.

        Returns:
            string: 8 hexadecimal values 0-F.
        """
        self._convert_status_to_bits()
        hexadecimals = self._get_hexadecimals(NUMBER_OF_HEXADECIMAL_CHARACTERS)
        return "".join(hexadecimals)

    def _convert_status_to_bits(self):
        for key, value in self._REFERENCE.items():
            if value == "Control mode":
                self._bits[2:4] = self._CONTROL_MODE[self._status["Control mode"]]
            elif value == "Update mode":
                self._bits[6:8] = self._UPDATE_MODE[self._status["Update mode"]]
            else:
                self._bits[int(key)] = self._status[value]

    def _get_hexadecimals(self, number_of_digits):
        bits = list(reversed(self._bits))

        return convert_to_hexadecimal(bits, number_of_digits)


def convert_to_hexadecimal(bits, padding):
    """Converts  bits to a hexadecimal character with padding.

    E.g.
        Converts [False, False, False, True], 0 to "1".
        Converts [True, False, False, False], 2 to "08"

    Args:
        bits: List of boolean values.
        padding: Integer of number of 0 padded places.

    Returns:
        string: Zero padded hexadecimal number.
    """
    bits_as_strings = ["1" if bit else "0" for bit in bits]

    bits_base_2 = int("".join(bits_as_strings), 2)

    zero_padded_eight_digit_hexadecimal_with_prefix = "{0:#0{1}x}".format(bits_base_2, padding + 2)

    zero_padded_eight_digit_hexadecimal_without_prefix = (
        zero_padded_eight_digit_hexadecimal_with_prefix[2:]
    )

    return zero_padded_eight_digit_hexadecimal_without_prefix.upper()
