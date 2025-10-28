from lewis.core import approaches
from lewis.core.statemachine import State

from .constants import HEATER_INDEX


class OffState(State):
    """Device is in off state.

    It does not display the temperature on the front it is not monitoring or controlling it.
    """

    NAME = "off"


class MonitorState(State):
    """Temperature is being monitored but heater is switched off."""

    NAME = "monitor"

    def in_state(self, dt):
        # heater is off because we are in monitor mode
        self._context.heater = 0


class ControlState(State):
    """Temperature is being controlled and monitored. The device will try to use the heater to make
    the temperature the same as the set point.
    """

    NAME = "control"

    def in_state(self, dt):
        device = self._context
        for output_index in range(device.sensor_count):
            sensor_source = (
                device.sensor_source[output_index] - 1
            )  # sensor source is 1 indexed
            try:
                temp = device.temperatures[sensor_source]
                setpoint = device.setpoints[output_index]
                device.temperatures[sensor_source] = approaches.linear(
                    temp, setpoint, 0.1, dt
                )
            except IndexError:
                # sensor source is out of range (probably 3)
                pass

        try:
            heater_sensor_source = device.sensor_source[HEATER_INDEX] - 1
            # set heater between 0 and 100% proportional to diff in temp * 10
            temp = device.temperatures[heater_sensor_source]
            setpoint = device.setpoints[HEATER_INDEX]
            diff_in_temp = setpoint - temp
            heater_limit = device.pid[HEATER_INDEX]["limit"]
            device.heater = max(0, min(diff_in_temp * 10.0, heater_limit))
        except IndexError:
            # heater is not connected to a sensor so it is off
            device.heater = 0
