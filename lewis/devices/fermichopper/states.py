from lewis.core import approaches
from lewis.core.statemachine import State


def check_speed(device):
    if device.get_true_speed() > 10 and not device.magneticbearing:
        device.is_broken = True


class DefaultState(State):
    def in_state(self, dt):
        check_speed(self._context)


class StoppingState(State):
    def in_state(self, dt):
        device = self._context

        rate = 0

        if not device.magneticbearing:
            rate += 1
        if device.drive:
            rate += 50

        device.set_true_speed(approaches.linear(device.get_true_speed(), 0, rate, dt))

        check_speed(device)


class GoingState(State):
    def in_state(self, dt):
        device = self._context

        rate = 0

        if device.drive:
            rate += 50
            if not device.magneticbearing:
                rate -= 1

        device.set_true_speed(
            approaches.linear(
                device.get_true_speed(), device.get_speed_setpoint(), rate, dt
            )
        )

        check_speed(device)


class StoppedState(State):
    def in_state(self, dt):
        check_speed(self._context)

    def on_entry(self, dt):
        self._context.drive = False
