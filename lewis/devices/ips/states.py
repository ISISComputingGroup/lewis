from lewis.devices.ips.modes import Activity

from lewis.core import approaches
from lewis.core.statemachine import State

SECS_PER_MIN = 60


class HeaterOnState(State):
    def in_state(self, dt):
        device = self._context

        device.heater_current = approaches.linear(
            device.heater_current, device.HEATER_ON_CURRENT, device.HEATER_RAMP_RATE, dt
        )

        # The magnet can only be ramped at a certain rate. The PSUs ramp rate can be varied.
        # If  the PSU attempts to ramp too fast for the magnet, then get a quench
        curr_ramp_rate = device.current_ramp_rate / SECS_PER_MIN

        if curr_ramp_rate > device.MAGNET_RAMP_RATE:
            device.quench("PSU ramp rate is too high")
        elif abs(device.current - device.magnet_current) > device.QUENCH_CURRENT_DELTA * dt:
            device.quench(
                "Difference between PSU current ({}) and magnet current ({}) is higher than allowed ({})".format(
                    device.current, device.magnet_current, device.QUENCH_CURRENT_DELTA * dt
                )
            )

        elif device.activity == Activity.TO_SETPOINT:
            device.current = approaches.linear(
                device.current, device.current_setpoint, curr_ramp_rate, dt
            )
            device.magnet_current = approaches.linear(
                device.magnet_current, device.current_setpoint, curr_ramp_rate, dt
            )

        elif device.activity == Activity.TO_ZERO:
            device.current = approaches.linear(device.current, 0, curr_ramp_rate, dt)
            device.magnet_current = approaches.linear(device.magnet_current, 0, curr_ramp_rate, dt)


class HeaterOffState(State):
    def in_state(self, dt):
        device = self._context

        device.heater_current = approaches.linear(
            device.heater_current, device.HEATER_OFF_CURRENT, device.HEATER_RAMP_RATE, dt
        )

        curr_ramp_rate = device.current_ramp_rate / SECS_PER_MIN

        # In this state, the magnet current is totally unaffected by whatever the PSU decides to do.
        if device.activity == Activity.TO_SETPOINT:
            device.current = approaches.linear(
                device.current, device.current_setpoint, curr_ramp_rate, dt
            )
        elif device.activity == Activity.TO_ZERO:
            device.current = approaches.linear(device.current, 0, curr_ramp_rate, dt)


class MagnetQuenchedState(State):
    pass
