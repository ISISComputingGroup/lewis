from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import ErrorStateCode, MovingState, StoppedState, WarnStateCode

HARD_LIMIT_MINIMUM = 0.0
HARD_LIMIT_MAXIMUM = 5000.0

# Defaults taken from device
DEVICE_DEFAULT_VELO = 52
DEVICE_DEFAULT_MAX_ACCEL = 10
DEVICE_DEFAULT_SPEED_RES = 190735

states = OrderedDict([("Stopped", StoppedState()), ("Moving", MovingState())])


class SimulatedLinmot(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.position = 0
        self.target_position = 0
        self.inside_hard_limits = True

        self.velocity = DEVICE_DEFAULT_VELO
        self.maximal_acceleration = DEVICE_DEFAULT_MAX_ACCEL
        self.speed_resolution = DEVICE_DEFAULT_SPEED_RES

        self.motor_warn_status = WarnStateCode.STATIONARY
        self.motor_error_status = ErrorStateCode.NONE

        self.new_action = False
        self.position_reached = False
        self.tolerance = 0.01

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (
                    ("Stopped", "Moving"),
                    lambda: self.new_action is True and self.position_reached is False,
                ),
                (("Moving", "Stopped"), lambda: self.position_reached is True),
            ]
        )

    @property
    def state(self):
        return self._csm.state

    @property
    def device_error(self):
        """Is the device errored due to being outside of the hard limits

        Return(s):
            (bool): True if device in errored state
        """
        return not self.within_hard_limits()

    @property
    def motor_warn_status_int(self):
        """Return the integer value of the warn status enum

        The state machine attempts to replicate the devices warn status codes. This is done via
        an enum, WarnStateCode, in the states.py: The enum is used for readability but the device
        only ever returns these integer codes.

        Return(s):
            (int): int value of the motor_warn_status
        """
        return self.motor_warn_status.value

    def move_to_target(self, target_position):
        """Demand the motor to drive to a target position.

        Argument(s):
            target_position (int): the desire axis target position
        """
        self.new_action = True
        self.position_reached = False
        self.target_position = target_position

    def within_hard_limits(self):
        """Determine if the axis position is within the physics limits of the devices capability.

        The axis has a range of moment, however if taken beyond these then it will put the controller into an
        error state.
        """
        return HARD_LIMIT_MINIMUM <= self.position <= HARD_LIMIT_MAXIMUM

    def _get_state_handlers(self):
        return states

    def _get_initial_state(self):
        return "Stopped"

    def reset(self):
        self._initialize_data()
