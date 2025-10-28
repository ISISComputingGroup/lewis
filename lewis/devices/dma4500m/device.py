from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DoneState, MeasuringState, ReadyState


class SimulatedDMA4500M(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.connected = True
        self.measurement_time = 0

        self.sample_id = 0
        self.target_temperature = 0.0
        self.actual_temperature = 0.0
        self.density = 0.0
        self.condition = "valid"

        self.data_buffer = ""
        self.status = ""

        self.measuring = False
        self.last_measurement_successful = False
        self.setting_temperature = False

    def reset(self):
        self._initialize_data()

    def start(self):
        if self.measuring:
            return "measurement already started"
        else:
            self.sample_id += 1
            self.measuring = True
            return "measurement started"

    def abort(self):
        if not self.measuring:
            return "measurement not started"
        else:
            self.measuring = False
            return "measurement aborted"

    def finished(self):
        return self.status

    def set_temperature(self, temperature):
        if self.measuring:
            return "not allowed during measurement"
        else:
            self.target_temperature = temperature
            self.setting_temperature = True
            return "accepted"

    def get_data(self):
        if not self.data_buffer:
            return "no new data"
        else:
            data = self.data_buffer
            self.data_buffer = ""
            return data

    def get_raw_data(self):
        sample_id = self.sample_id if self.sample_id else "NaN"
        return "{0:.6f};{1:.2f};{2:.2f};{3}".format(
            self.density, self.actual_temperature, self.target_temperature, sample_id
        )

    def _get_state_handlers(self):
        return {
            "ready": ReadyState(),
            "measuring": MeasuringState(),
            "done": DoneState(),
        }

    def _get_initial_state(self):
        return "ready"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("ready", "measuring"), lambda: self.measuring is True),
                (
                    ("measuring", "ready"),
                    lambda: self.measuring is False and not self.last_measurement_successful,
                ),
                (
                    ("measuring", "done"),
                    lambda: self.measuring is False and self.last_measurement_successful,
                ),
                (("done", "measuring"), lambda: self.measuring is True),
                (("done", "ready"), lambda: self.setting_temperature is True),
                (("ready", "ready"), lambda: self.setting_temperature is True),
            ]
        )
