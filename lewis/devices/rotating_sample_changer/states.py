from lewis.core import approaches
from lewis.core.statemachine import State


class Errors(object):
    NO_ERR = 0
    ERR_INV_DEST = 5
    ERR_NOT_INITIALISED = 6
    ERR_ARM_DROPPED = 7
    ERR_ARM_FAILED_TO_LOWER = 8
    ERR_ARM_UP = 8
    ERR_CANT_ROT_IF_NOT_UP = 10


class MovingState(State):
    def on_entry(self, dt):
        self._context.arm_lowered = False

    def in_state(self, dt):
        self._context.car_pos = approaches.linear(
            self._context.car_pos, self._context.car_target, self._context.CAR_SPEED, dt
        )

    def on_exit(self, dt):
        self._context.arm_lowered = True


class SampleDroppedState(State):
    def on_entry(self, dt):
        self._context.log.info("Entered sample dropped state.")
        self._context.current_err = Errors.ERR_ARM_DROPPED
        self._context.car_target = self._context.car_pos

    def on_exit(self, dt):
        self._context.current_err = Errors.NO_ERR
        self._context.log.info("Exited sample dropped state.")
