from lewis.core import approaches
from lewis.core.statemachine import State


class TemperatureControlState(State):
    def in_state(self, dt):
        device = self._context

        rate = 10

        device.he3pot_temp = approaches.linear(
            device.he3pot_temp, device.temperature_sp, rate, dt
        )


class He3PotEmptyState(State):
    def in_state(self, dt):
        device = self._context

        device.he3pot_temp = approaches.linear(
            device.he3pot_temp, device.drift_towards, device.drift_rate, dt
        )


class RegeneratingState(State):
    def in_state(self, dt):
        device = self._context

        device.sorb_temp = approaches.linear(
            device.sorb_temp, device.temperature_sp, device.heater_voltage, dt
        )
        device.he3pot_temp = approaches.linear(
            device.he3pot_temp, device.drift_towards, device.drift_rate, dt
        )
