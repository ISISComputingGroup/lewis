from lewis.core.statemachine import State


class ReadyState(State):
    def on_entry(self, dt):
        self._context.status = "measurement not started"
        self._context.actual_temperature = self._context.target_temperature
        self._context.setting_temperature = False


class MeasuringState(State):
    time_elapsed = 0.0

    def on_entry(self, dt):
        self._context.status = "measurement not finished"
        self._context.last_measurement_successful = False
        self.time_elapsed = 0.0

    def in_state(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed > self._context.measurement_time:
            self._context.last_measurement_successful = True
            self._context.measuring = False

    def on_exit(self, dt):
        if not self._context.last_measurement_successful:
            self._context.condition = "canceled"
            self._context.data_buffer = "data: ---;---;canceled"
        else:
            self._context.condition = "valid"
            self._context.data_buffer = "data: {0:.5f};{1:.2f};{2}".format(
                self._context.density, self._context.actual_temperature, self._context.condition
            )


class DoneState(State):
    def on_entry(self, dt):
        self._context.status = "measurement finished"
