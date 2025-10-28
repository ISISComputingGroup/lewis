from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState, GoingState, StoppingState


class SimulatedSkfMb350Chopper(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self._started = False
        self.phase = 0
        self.frequency = 0
        self.frequency_setpoint = 0
        self.phase_percent_ok = 100.0
        self.phase_repeatability = 100.0

        self.interlocks = OrderedDict(
            [
                ("DSP_WD_FAIL", False),
                ("OSCILLATOR_FAIL", False),
                ("POSITION_SHUTDOWN", False),
                ("EMERGENCY_STOP", False),
                ("UPS_FAIL", False),
                ("EXTERNAL_FAULT", False),
                ("CC_WD_FAIL", False),
                ("OVERSPEED_TRIP", False),
                ("VACUUM_FAIL", False),
                ("MOTOR_OVER_TEMP", False),
                ("REFERENCE_SIGNAL_LOSS", False),
                ("SPEED_SENSOR_LOSS", False),
                ("COOLING_LOSS", False),
                ("DSP_SUMMARY_SHUTDOWN", False),
                ("CC_SHUTDOWN_REQ", False),
                ("TEST_MODE", False),
            ]
        )

        self.rotator_angle = 90

    def set_interlock_state(self, item, value):
        self.interlocks[item] = value

    def get_interlocks(self):
        return self.interlocks

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
            "going": GoingState(),
            "stopping": StoppingState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (
                    ("default", "going"),
                    lambda: self.frequency_setpoint != self.frequency and self._started,
                ),
                (("going", "stopping"), lambda: not self._started),
                (
                    ("stopping", "default"),
                    lambda: self.frequency == 0 and not self._started,
                ),
            ]
        )

    def set_frequency(self, frequency):
        self.frequency_setpoint = frequency

    def get_frequency(self):
        return self.frequency

    def set_nominal_phase(self, phase):
        self.phase = phase

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def is_controller_ok(self):
        return True

    def is_up_to_speed(self):
        return self.frequency == self.frequency_setpoint and self._started

    def is_able_to_run(self):
        return True

    def is_shutting_down(self):
        return False

    def is_levitation_complete(self):
        return self.is_up_to_speed()  # Not really the correct condition but close enough

    def is_phase_locked(self):
        return self.is_up_to_speed()  # Not really the correct condition but close enough

    def get_motor_direction(self):
        return 1  # Not clear if this can be set externally or only from front panel of physical device.

    def is_avc_on(self):
        return True  # Don't know what this is/represents. Manual doesn't help.

    def get_phase(self):
        return self.phase

    def get_phase_percent_ok(self):
        return self.phase_percent_ok

    def get_phase_repeatability(self):
        return self.phase_repeatability

    def set_phase_repeatability(self, value):
        self.phase_repeatability = value

    def get_rotator_angle(self):
        return self.rotator_angle

    def set_rotator_angle(self, angle):
        self.rotator_angle = angle
