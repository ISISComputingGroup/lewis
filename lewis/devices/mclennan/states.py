from lewis.core.statemachine import State


class StoppedState(State):
    def on_entry(self, dt):
        device = self._context
        self.log.info("Entering STOPPED state")
        device.current_op = "Stopping"
        device.current_op = "Idle"
        device.is_idle = True


class JoggingState(State):
    def on_entry(self, dt):
        device = self._context
        self.log.info("Entering JOGGING state")
        device.current_op = "Constant velocity"
        device.is_idle = False

    def in_state(self, dt):
        device = self._context
        device.is_idle = False
        device.position += device.jog_velocity * dt


class MovingState(State):
    def __init__(self):
        self.incr = 0

    def on_entry(self, dt):
        device = self._context
        self.log.info("Entering MOVING state")
        device.current_op = "Move"
        self.incr = (device.target_position - device.position) / 5.0
        device.is_idle = False

    def in_state(self, dt):
        device = self._context
        device.position += self.incr
        device.is_idle = False
        if device.position == device.target_position:
            device.is_moving = False


#        device.position += device.jog_velocity * dt


class HomingState(State):
    def __init__(self):
        self.incr = 0

    def on_entry(self, dt):
        device = self._context
        self.log.info("Entering HOMING state")
        device.current_op = "Home to datum"
        self.incr = 0
        device.is_idle = False

    def in_state(self, dt):
        device = self._context
        self.incr += 1
        device.is_idle = False
        if self.incr < 5:
            device.position += 10
        else:
            device.position = 0
            device.is_homing = False


#        device.position += device.jog_velocity * dt
