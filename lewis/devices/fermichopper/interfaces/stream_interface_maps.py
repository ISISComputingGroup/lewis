from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log

from ..device import ChopperParameters
from .common_interface_utils import COMMANDS

TIMING_FREQ_MHZ = 18.0


class JulichChecksum(object):
    @staticmethod
    def _calculate(alldata):
        """Calculates the Julich checksum of the given data
        :param alldata: the input data (list of chars, length 5)
        :return: the Julich checksum of the given input data
        """
        assert all(i in list("#0123456789ABCDEFGH") for i in alldata), (
            "Invalid character can't calculate checksum"
        )
        return (
            "00"
            if all(x in ["0", "#"] for x in alldata)
            else hex(sum(ord(i) for i in alldata[1:])).upper()[-2:]
        )

    @staticmethod
    def verify(header, data, actual_checksum):
        """Verifies that the checksum of received data is correct.
        :param header: The leading # and the first byte (str, length 2)
        :param data: The data bytes (str, length 4)
        :param actual_checksum: The transmitted checksum (str, length 2)
        :return: Nothing
        :raises: AssertionError: If the checksum didn't match or the inputs were invalid
        """
        assert len(header) == 2, "Header should have length 2"
        assert len(data) == 4, "Data should have length 4"
        assert len(actual_checksum) == 2, "Actual checksum should have length 2"
        assert JulichChecksum._calculate(header + data) == actual_checksum, "Checksum did not match"

    @staticmethod
    def append(data):
        """Utility method for appending the Julich checksum to the input data
        :param data: the input data
        :return: the input data with it's checksum appended
        """
        assert len(data) == 6, "Unexpected data length."
        return data + JulichChecksum._calculate(data)


@has_log
class FermichopperStreamInterface(StreamInterface):
    protocol = "fermi_maps"

    commands = COMMANDS

    in_terminator = "$"
    out_terminator = ""

    def build_status_code(self):
        status = 0

        if True:  # Microcontroller OK?
            status += 1
        if self._device.get_true_speed() == self._device.get_speed_setpoint():
            status += 2
        if self._device.magneticbearing:
            status += 8
        if self._device.get_voltage() > 0:
            status += 16
        if self._device.drive:
            status += 32
        if self._device.parameters == ChopperParameters.MERLIN_LARGE:
            status += 64
        if False:  # Interlock open?
            status += 128
        if self._device.parameters == ChopperParameters.HET_MARI:
            status += 256
        if self._device.parameters == ChopperParameters.MERLIN_SMALL:
            status += 512
        if self._device.speed > 600:
            status += 1024
        if self._device.speed > 10 and not self._device.magneticbearing:
            status += 2048
        if any(
            abs(voltage) > 3
            for voltage in [
                self._device.autozero_1_lower,
                self._device.autozero_2_lower,
                self._device.autozero_1_upper,
                self._device.autozero_2_upper,
            ]
        ):
            status += 4096

        return status

    def handle_error(self, request, error):
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))
        return str(error)

    def get_all_data(self, checksum):
        JulichChecksum.verify("#0", "0000", checksum)

        def autozero_calibrate(value):
            return (value + 7.0) / 0.0137

        return (
            JulichChecksum.append("#1" + self._device.get_last_command())
            + JulichChecksum.append("#2{:04X}".format(self.build_status_code()))
            + JulichChecksum.append(
                "#3{:04X}".format(int(round(self._device.get_speed_setpoint() * 60)))
            )
            + JulichChecksum.append(
                "#4{:04X}".format(int(round(self._device.get_true_speed() * 60)))
            )
            + JulichChecksum.append(
                "#5{:04X}".format(
                    int(round((self._device.get_nominal_delay() * TIMING_FREQ_MHZ) % 65536))
                )
            )
            + JulichChecksum.append(
                "#6{:04X}".format(
                    int(round((self._device.get_nominal_delay() * TIMING_FREQ_MHZ) / 65536))
                )
            )
            + JulichChecksum.append(
                "#7{:04X}".format(
                    int(round((self._device.get_actual_delay() * TIMING_FREQ_MHZ) % 65536))
                )
            )
            + JulichChecksum.append(
                "#8{:04X}".format(
                    int(round((self._device.get_actual_delay() * TIMING_FREQ_MHZ) / 65536))
                )
            )
            + JulichChecksum.append(
                "#9{:04X}".format(int(round(self._device.get_gate_width() * TIMING_FREQ_MHZ)))
            )
            + JulichChecksum.append(
                "#A{:04X}".format(int(round(self._device.get_current() / 0.00684)))
            )
            + JulichChecksum.append(
                "#B{:04X}".format(int(round(autozero_calibrate(self._device.autozero_1_upper))))
            )
            + JulichChecksum.append(
                "#C{:04X}".format(int(round(autozero_calibrate(self._device.autozero_2_upper))))
            )
            + JulichChecksum.append(
                "#D{:04X}".format(int(round(autozero_calibrate(self._device.autozero_1_lower))))
            )
            + JulichChecksum.append(
                "#E{:04X}".format(int(round(autozero_calibrate(self._device.autozero_2_lower))))
            )
            + "$"
        )

    def execute_command(self, command, checksum):
        JulichChecksum.verify("#1", command, checksum)
        self._device.do_command(command)

    def set_speed(self, command, checksum):
        JulichChecksum.verify("#3", command, checksum)
        self._device.set_speed_setpoint(int(command, 16) / 60)

    def set_delay_lowword(self, command, checksum):
        JulichChecksum.verify("#5", command, checksum)
        self._device.set_delay_lowword(int(command, 16) / TIMING_FREQ_MHZ)

    def set_delay_highword(self, command, checksum):
        JulichChecksum.verify("#6", command, checksum)
        self._device.set_delay_highword(int(command, 16) / TIMING_FREQ_MHZ)

    def set_gate_width(self, command, checksum):
        JulichChecksum.verify("#9", command, checksum)
        self._device.set_gate_width(int(command, 16) / TIMING_FREQ_MHZ)
