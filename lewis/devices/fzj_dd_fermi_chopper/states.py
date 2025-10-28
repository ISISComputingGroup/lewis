from lewis.core import approaches
from lewis.core.statemachine import State

# FZJ Digital Drive Fermi Chopper Controller


class StartedState(State):
    """Device is in started state."""

    NAME = "Started"

    def in_state(self, dt):
        device = self._context
        device.frequency = approaches.linear(
            device.frequency, device.frequency_setpoint, 1, dt
        )
        device.phase = approaches.linear(device.phase, device.phase_setpoint, 1, dt)


class StoppedState(State):
    """Device is in stopped state."""

    NAME = "Stopped"

    def in_state(self, dt):
        device = self._context
        device.frequency = approaches.linear(device.frequency, 0, 1, dt)
        device.phase = approaches.linear(device.phase, 0, 1, dt)
