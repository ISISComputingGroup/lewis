from lewis.core.logging import has_log
from lewis.core.statemachine import State


@has_log
class DefaultState(State):
    def in_state(self, dt):
        device = self._context

        if device.interlock_is_triggered and device.shutter_is_open:
            self.log.info("INTERLOCK close shutter")
            device.shutter_is_open = False
