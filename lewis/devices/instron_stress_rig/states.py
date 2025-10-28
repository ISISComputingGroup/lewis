import time

from lewis.core import approaches
from lewis.core.statemachine import State


class DefaultState(State):
    def in_state(self, dt):
        device = self._context
        device.set_current_time()

        if (
            device.watchdog_refresh_time + 3 < time.time()
            and device.get_control_mode() != 0
        ):
            print("Watchdog time expired, going back to front panel control mode")
            device.set_control_mode(0)

        device.stop_waveform_generation_if_requested()


class GoingToSetpointState(DefaultState):
    def in_state(self, dt):
        super(GoingToSetpointState, self).in_state(dt)
        device = self._context
        device.channels[device.control_channel].value = approaches.linear(
            device.channels[device.control_channel].value,
            device.channels[device.control_channel].ramp_amplitude_setpoint,
            0.001,
            dt,
        )

    def on_exit(self, dt):
        device = self._context
        device.movement_type = 0


class GeneratingWaveformState(DefaultState):
    TIME_SINCE_LAST_QUART_COUNT = 0

    @staticmethod
    def increment_cycle(device, dt):
        GeneratingWaveformState.TIME_SINCE_LAST_QUART_COUNT += dt
        if GeneratingWaveformState.TIME_SINCE_LAST_QUART_COUNT > 1.0:
            GeneratingWaveformState.TIME_SINCE_LAST_QUART_COUNT = 0.0
            device.quarter_cycle_event()

    def in_state(self, dt):
        super(GeneratingWaveformState, self).in_state(dt)
        device = self._context

        GeneratingWaveformState.increment_cycle(device, dt)
        device.channels[device.control_channel].value = device.get_waveform_value()
