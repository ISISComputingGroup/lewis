from .sensor import Sensor
from .sensor_status import SensorStatus


class PressureSensor(Sensor):
    """A sensor that reads the pressure.
    """

    def __init__(self):
        super(PressureSensor, self).__init__()

    def set_value(self, v, target):
        """Updates the pressure reading with a new value along with the sensor's status.

        :param v: The new value
        :param target: The target/limit value
        """
        super(PressureSensor, self).set_value(v)
        if self._value < 0.0:
            self._status = SensorStatus.VALUE_TOO_LOW
        elif self._value > target:
            self._status = SensorStatus.VALUE_TOO_HIGH
        else:
            self._status = SensorStatus.VALUE_IN_RANGE
