from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .chopper_type import ChopperType
from .states import MAX_TEMPERATURE, DefaultInitState, DefaultStartedState, DefaultStoppedState


class SimulatedMk2Chopper(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self._type = ChopperType(50, ChopperType.INDRAMAT)

        self._demanded_frequency = self._type.get_frequency()
        self._max_phase_delay = self._type.get_max_phase_for_closest_frequency(
            self._demanded_frequency
        )
        self._true_frequency = 0

        self._demanded_phase_delay = 0
        self._true_phase_delay = 0

        self._demanded_phase_error_window = 1

        self._started = False
        self._fault = False

        self._phase_delay_error = False

        self._temperature = 0

        # When initialisation is complete, this is set to true and the device will enter a running state
        self.ready = True

    def _get_state_handlers(self):
        return {
            "init": DefaultInitState(),
            "stopped": DefaultStoppedState(),
            "started": DefaultStartedState(),
        }

    def _get_initial_state(self):
        return "init"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("init", "stopped"), lambda: self.ready),
                (("stopped", "started"), lambda: self._started is True),
                (("started", "stopped"), lambda: self._started is False),
            ]
        )

    def get_system_frequency(self):
        return self._type.get_frequency()

    def get_manufacturer(self):
        return self._type.get_manufacturer()

    def get_demanded_frequency(self):
        return self._demanded_frequency

    def get_true_frequency(self):
        return self._true_frequency

    def get_demanded_phase_delay(self):
        return self._demanded_phase_delay

    def get_true_phase_delay(self):
        return self._true_phase_delay

    def get_demanded_phase_error_window(self):
        return self._demanded_phase_error_window

    def get_true_phase_error(self):
        return abs(self._true_phase_delay - self._demanded_phase_delay)

    def get_temperature(self):
        return self._temperature

    def inverter_ready(self):
        return self._type.get_manufacturer() in [ChopperType.CORTINA]

    def motor_running(self):
        return self._started

    def in_sync(self):
        tolerance = 0.001 * self._type.get_frequency()
        return abs(self._true_frequency - self._demanded_frequency) < tolerance

    def reg_mode(self):
        return False

    def external_fault(self):
        return self._fault

    def clock_loss(self):
        return False

    def bearing_1_overheat(self):
        return self._overheat()

    def bearing_2_overheat(self):
        return self._overheat()

    def motor_overheat(self):
        return self._overheat()

    def _overheat(self):
        return self._temperature > MAX_TEMPERATURE

    def chopper_overspeed(self):
        return self._true_frequency > self._type.get_frequency()

    def phase_delay_error(self):
        return self._phase_delay_error

    def phase_delay_correction_error(self):
        tolerance = 0.001 * self._demanded_phase_delay
        return abs(self._true_phase_delay - self._demanded_phase_delay) > tolerance

    def phase_accuracy_window_error(self):
        return (
            abs(self._true_phase_delay - self._demanded_phase_delay)
            > self._demanded_phase_error_window
        )

    def set_demanded_frequency(self, new_frequency_int):
        self._demanded_frequency = self._type.get_closest_valid_frequency(new_frequency_int)
        self._max_phase_delay = self._type.get_max_phase_for_closest_frequency(new_frequency_int)

    def set_demanded_phase_delay(self, new_phase_delay):
        self._demanded_phase_delay = min(new_phase_delay, self._max_phase_delay)
        self._phase_delay_error = self._demanded_phase_delay != new_phase_delay

    def set_demanded_phase_error_window(self, new_phase_window):
        self._demanded_phase_error_window = new_phase_window

    def set_true_frequency(self, new_frequency):
        self._true_frequency = new_frequency

    def set_true_phase_delay(self, new_delay):
        self._true_phase_delay = new_delay

    def set_chopper_type(self, frequency, manufacturer):
        self._type = ChopperType(frequency, manufacturer)
        # Do this in case the current demanded frequency is invalid for the new type
        self.set_demanded_frequency(self._demanded_frequency)

    def set_temperature(self, temperature):
        self._temperature = temperature

    def start(self):
        self._started = True

    def stop(self):
        self._started = False
