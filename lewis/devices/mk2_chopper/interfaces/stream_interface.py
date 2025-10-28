from lewis.adapters.stream import Cmd, StreamInterface

from ..chopper_type import ChopperType


def filled_int(val, length):
    """Takes a value and returns a zero padded representation of the integer component.

    :param val: The original value.
    :param length: Minimum length of the returned string
    :return: Zero-padded integer representation (if possible) of string. Original string used if integer conversion
    fails
    """
    try:
        converted_val = int(val)
    except ValueError:
        converted_val = val
    return str(converted_val).zfill(length)


class Mk2ChopperStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        Cmd("get_true_frequency", "^RF$"),
        Cmd("get_demanded_frequency", "^RG$"),
        Cmd("get_true_phase_delay", "^RP$"),
        Cmd("get_demanded_phase_delay", "^RQ$"),
        Cmd("get_true_phase_error", "^RE$"),
        Cmd("get_demanded_phase_error_window", "^RW$"),
        Cmd("get_chopper_interlocks", "^RC$"),
        Cmd("get_spectral_interlocks", "^RS$"),
        Cmd("get_error_flags", "^RX$"),
        Cmd("read_all", "^RA$"),
        Cmd("set_chopper_started", "^WS([0-9]+)$"),
        Cmd("set_demanded_frequency", "^WM([0-9]+)$"),
        Cmd("set_demanded_phase_delay", "^WP([0-9]+)$"),
        Cmd("set_demanded_phase_error_window", "^WR([0-9]+)$"),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
        return str(error)

    def get_demanded_frequency(self):
        return "RG{0}".format(filled_int(self._device.get_demanded_frequency(), 3))

    def get_true_frequency(self):
        return "RF{0}".format(filled_int(self._device.get_true_frequency(), 3))

    def get_demanded_phase_delay(self):
        return "RQ{0}".format(filled_int(self._device.get_demanded_phase_delay(), 5))

    def get_true_phase_delay(self):
        return "RP{0}".format(filled_int(self._device.get_true_phase_delay(), 5))

    def get_demanded_phase_error_window(self):
        return "RW{0}".format(filled_int(self._device.get_demanded_phase_error_window(), 3))

    def get_true_phase_error(self):
        return "RE{0}".format(filled_int(self._device.get_true_phase_error(), 3))

    def get_spectral_interlocks(self):
        bits = [0] * 8
        if self._device.get_manufacturer() == ChopperType.CORTINA:
            bits[0] = 1 if self._device.inverter_ready() else 0
            bits[1] = 1 if self._device.motor_running() else 0
            bits[2] = 1 if self._device.in_sync() else 0
        elif self._device.get_manufacturer() == ChopperType.INDRAMAT:
            bits[0] = 1 if self._device.motor_running() else 0
            bits[1] = 1 if self._device.reg_mode() else 0
            bits[2] = 1 if self._device.in_sync() else 0
        elif self._device.get_manufacturer() == ChopperType.SPECTRAL:
            bits[2] = 1 if self._device.external_fault() else 0
        return "RS{0:8s}".format(Mk2ChopperStreamInterface._string_from_bits(bits))

    def get_chopper_interlocks(self):
        bits = [0] * 8
        bits[0] = 1 if self._device.get_system_frequency() == 50 else 0
        bits[1] = 1 if self._device.clock_loss() else 0
        bits[2] = 1 if self._device.bearing_1_overheat() else 0
        bits[3] = 1 if self._device.bearing_2_overheat() else 0
        bits[4] = 1 if self._device.motor_overheat() else 0
        bits[5] = 1 if self._device.chopper_overspeed() else 0
        return "RC{0:8s}".format(Mk2ChopperStreamInterface._string_from_bits(bits))

    def get_error_flags(self):
        bits = [0] * 8
        bits[0] = 1 if self._device.phase_delay_error() else 0
        bits[1] = 1 if self._device.phase_delay_correction_error() else 0
        bits[2] = 1 if self._device.phase_accuracy_window_error() else 0
        return "RX{0:8s}".format(Mk2ChopperStreamInterface._string_from_bits(bits))

    def get_manufacturer(self):
        return self._type.get_manufacturer()

    def set_chopper_started(self, start_flag_raw):
        try:
            start_flag = int(start_flag_raw)
        except ValueError:
            pass
        else:
            if start_flag == 1:
                self._device.start()
            elif start_flag == 2:
                self._device.stop()
        return

    def set_demanded_frequency(self, new_frequency_raw):
        return Mk2ChopperStreamInterface._set(
            new_frequency_raw, self.get_demanded_frequency, self._device.set_demanded_frequency
        )

    def set_demanded_phase_delay(self, new_phase_delay_raw):
        return Mk2ChopperStreamInterface._set(
            new_phase_delay_raw,
            self.get_demanded_phase_delay,
            self._device.set_demanded_phase_delay,
        )

    def set_demanded_phase_error_window(self, new_phase_error_window_raw):
        return Mk2ChopperStreamInterface._set(
            new_phase_error_window_raw,
            self.get_demanded_phase_error_window,
            self._device.set_demanded_phase_error_window,
        )

    def read_all(self):
        return "RA:Don't use, it causes the driver to lock up"

    @staticmethod
    def _set(raw, device_get, device_set):
        try:
            int_value = int(raw)
        except ValueError:
            pass
        else:
            device_set(int_value)
        return device_get()

    @staticmethod
    def _string_from_bits(bits):
        return "".join(str(n) for n in reversed(bits))
