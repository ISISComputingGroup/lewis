from lewis.devices import Device


class SimulatedAG33220A(Device):
    """Simulated AG33220A"""

    connected = True

    # Constants
    AMP_MIN = 0.01
    AMP_MAX = 10
    OFF_MAX = 4.995
    VOLT_MAX = 5
    VOLT_MIN = -5
    VOLT_LOW_MAX = 4.99
    VOLT_HIGH_MIN = -4.99
    VOLT_PRECISION = 0.01
    FREQ_MINS = {
        "SIN": 10**-6,
        "SQU": 10**-6,
        "RAMP": 10**-6,
        "PULS": 5 * 10**-4,
        "NOIS": 10**-6,
        "USER": 10**-6,
    }
    FREQ_MAXS = {
        "SIN": 2 * 10**7,
        "SQU": 2 * 10**7,
        "RAMP": 2 * 10**5,
        "PULS": 5 * 10**6,
        "NOIS": 2 * 10**7,
        "USER": 6 * 10**6,
    }

    # Device variables
    idn = "Agilent Technologies,33220A-MY44033103,2.02-2.02-22-2"
    amplitude = 0.1
    frequency = 1000
    offset = 0
    units = "VPP"
    function = "SIN"
    output = "ON"
    voltage_high = 0.05
    voltage_low = -0.05
    range_auto = "OFF"

    def limit(self, value, minimum, maximum):
        """Limits an input number between two given numbers or sets the value to the maximum or minimum.

        :param value: the value to be limited
        :param minimum: the smallest that the value can be
        :param maximum: the largest that the value can be

        :return: the value after it has been limited
        """
        if type(value) is str:
            try:
                value = float(value)
            except ValueError:
                return {"MIN": minimum, "MAX": maximum}[value]

        return max(min(value, maximum), minimum)

    def set_new_amplitude(self, new_amplitude):
        """Changing the amplitude to the new amplitude whilst also changing the offset if voltage high or low is
        outside the boundary. The volt high and low are then updated.

        :param new_amplitude: the amplitude to set the devices amplitude to
        """
        new_amplitude = self.limit(new_amplitude, self.AMP_MIN, self.AMP_MAX)

        peak_amp = 0.5 * new_amplitude
        if self.offset + peak_amp > self.VOLT_MAX:
            self.offset = self.VOLT_MAX - peak_amp
        elif self.offset - peak_amp < self.VOLT_MIN:
            self.offset = self.VOLT_MIN + peak_amp

        self.amplitude = new_amplitude

        self._update_volt_high_and_low(self.amplitude, self.offset)

    def set_new_frequency(self, new_frequency):
        """Sets the frequency within limits between upper and lower bound (depends on the function).

        :param new_frequency: the frequency to set to
        """
        self.frequency = self.limit(
            new_frequency, self.FREQ_MINS[self.function], self.FREQ_MAXS[self.function]
        )

    def set_new_voltage_high(self, new_voltage_high):
        """Sets a new voltage high which then changes the voltage low to keep it lower.
        The voltage offset and amplitude are then updated.

        :param new_voltage_high: the value of voltage high to set to
        """
        new_voltage_high = self.limit(new_voltage_high, self.VOLT_HIGH_MIN, self.VOLT_MAX)
        if new_voltage_high <= self.voltage_low:
            self.voltage_low = self.limit(
                new_voltage_high - self.VOLT_PRECISION, self.VOLT_MIN, new_voltage_high
            )
        self._update_volt_and_offs(self.voltage_low, new_voltage_high)

    def set_new_voltage_low(self, new_voltage_low):
        """Sets a new voltage high which then changes the voltage low to keep it higher.
        The voltage offset and amplitude are then updated.

        :param new_voltage_low: the value of voltage low which is to be set
        """
        new_voltage_low = self.limit(new_voltage_low, self.VOLT_MIN, self.VOLT_LOW_MAX)
        if new_voltage_low >= self.voltage_high:
            self.voltage_high = self.limit(
                new_voltage_low + self.VOLT_PRECISION, new_voltage_low, self.VOLT_MAX
            )
        self._update_volt_and_offs(new_voltage_low, self.voltage_high)

    def _update_volt_and_offs(self, new_low, new_high):
        """Updates the value of amplitude and offset if there is a change in voltage low or voltage high.

        :param new_low: the value of voltage low
        :param new_high: the value of voltage high
        """
        self.voltage_high = new_high
        self.voltage_low = new_low
        self.amplitude = self.voltage_high - self.voltage_low
        self.offset = (self.voltage_high + self.voltage_low) / 2

    def set_offs_and_update_voltage(self, new_offset):
        """Sets the value of offset and updates the amplitude, voltage low and voltage high for a new value of the offset.

        :param new_offset: the new offset to be set
        """
        new_offset = self.limit(new_offset, -self.OFF_MAX, self.OFF_MAX)
        if new_offset + self.voltage_high > self.VOLT_MAX:
            self.amplitude = 2 * (self.VOLT_MAX - new_offset)
            self.voltage_high = self.VOLT_MAX
            self.voltage_low = self.VOLT_MAX - self.amplitude
        elif new_offset + self.voltage_low < self.VOLT_MIN:
            self.amplitude = 2 * (self.VOLT_MIN - new_offset)
            self.voltage_low = self.VOLT_MIN
            self.voltage_high = self.VOLT_MIN + self.amplitude
        else:
            self._update_volt_high_and_low(self.amplitude, new_offset)
        self.offset = new_offset

    def _update_volt_high_and_low(self, new_volt, new_offs):
        """Updates the value of voltage high and low for a given value of amplitude and offset.

        :param new_volt: the value of the amplitude
        :param new_offs: the value of the offset
        """
        self.offset = new_offs
        self.amplitude = new_volt
        self.voltage_high = new_offs + new_volt / 2
        self.voltage_low = new_offs - new_volt / 2

    def get_output(self):
        return ["OFF", "ON"].index(self.output)

    def get_range_auto(self):
        possible_ranges = ["OFF", "ON", "ONCE"]
        return possible_ranges.index(self.range_auto)

    def set_function(self, new_function):
        self.function = new_function
        self.frequency = self.limit(
            self.frequency, self.FREQ_MINS[new_function], self.FREQ_MAXS[new_function]
        )
