class ChopperType(object):
    """A type of chopper that the system can represent. Typically MK2 choppers come in 50Hz and 100Hz varieties.
    """

    # An overspeed system state used to check the overspeed error flag
    OVERSPEED = (999, 95)

    # A dictionary of states the system can be in {Maximum frequency: [(Actual frequency, Max phase delay), ...]}
    VALID_SYSTEM_STATES = {
        50: [
            (5, 99995),
            (10, 99995),
            (12.5, 79995),
            (16.67, 59995),
            (25, 39995),
            (50, 19995),
            OVERSPEED,
        ],
        100: [(12.5, 79995), (25, 39995), (50, 19995), (100, 9995), OVERSPEED],
    }

    CORTINA = "cortina"
    INDRAMAT = "indramat"
    SPECTRAL = "spectral"
    MANUFACTURERS = [CORTINA, INDRAMAT, SPECTRAL]

    def __init__(self, max_frequency, manufacturer):
        possible_max_frequencies = ChopperType.VALID_SYSTEM_STATES.keys()
        self._max_frequency = (
            max_frequency
            if max_frequency in possible_max_frequencies
            else min(possible_max_frequencies)
        )

        manufacturer_low = manufacturer.lower()
        self._manufacturer = (
            manufacturer_low
            if manufacturer_low in ChopperType.MANUFACTURERS
            else ChopperType.INDRAMAT
        )

    def get_closest_valid_frequency(self, frequency):
        return self._get_frequency_and_phase_closest_to_frequency(frequency)[0]

    def get_max_phase_for_closest_frequency(self, frequency):
        return self._get_frequency_and_phase_closest_to_frequency(frequency)[1]

    def _get_frequency_and_phase_closest_to_frequency(self, frequency):
        return min(
            ChopperType.VALID_SYSTEM_STATES[self._max_frequency],
            key=lambda x: abs(x[0] - frequency),
        )

    def get_manufacturer(self):
        return self._manufacturer

    def get_frequency(self):
        return self._max_frequency
