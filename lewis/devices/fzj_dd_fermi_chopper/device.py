from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import StartedState, StoppedState


class SimulatedFZJDDFCH(StateMachineDevice):
    """Simulated FZJ Digital Drive Fermi Chopper Controller.
    """

    def _initialize_data(self):
        """Sets the initial state of the device.
        """
        self.chopper_name = "C01"  # only one chopper in this case
        self.frequency_reference = 50  # reference frequency set to 50Hz to match actual device
        self.frequency_setpoint = 0
        self.frequency = 0
        self.phase_setpoint = 0
        self.phase = 0
        self.phase_status_is_ok = False
        self.magnetic_bearing_is_on = False
        self.magnetic_bearing_status_is_ok = False
        self.drive_is_on = False
        self.drive_mode_is_start = False
        self.drive_l1_current = 0
        self.drive_l2_current = 0
        self.drive_l3_current = 0
        self.drive_direction_is_cw = False
        self.drive_temperature = 0
        self.phase_outage = 0
        self.master_chopper = "C1"
        self.logging_is_on = False
        self.dsp_status_is_ok = False
        self.interlock_er_status_is_ok = False
        self.interlock_vacuum_status_is_ok = False
        self.interlock_frequency_monitoring_status_is_ok = False
        self.interlock_magnetic_bearing_amplifier_temperature_status_is_ok = False
        self.interlock_magnetic_bearing_amplifier_current_status_is_ok = False
        self.interlock_drive_amplifier_temperature_status_is_ok = False
        self.interlock_drive_amplifier_current_status_is_ok = False
        self.interlock_ups_status_is_ok = False

        self.error_on_set_frequency = None
        self.error_on_set_phase = None
        self.error_on_set_magnetic_bearing = None
        self.error_on_set_drive_mode = None

        self.connected = True

    def _get_state_handlers(self):
        """Returns: states and their names
        """
        return {StartedState.NAME: StartedState(), StoppedState.NAME: StoppedState()}

    def _get_initial_state(self):
        """Returns: the name of the initial state
        """
        return StoppedState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions
        """
        return OrderedDict(
            [
                ((StoppedState.NAME, StartedState.NAME), lambda: self.drive_mode_is_start),
                ((StartedState.NAME, StoppedState.NAME), lambda: not self.drive_mode_is_start),
            ]
        )

    def reset(self):
        """Reset device to defaults
        :return:
        """
        self._initialize_data()
