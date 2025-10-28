from lewis.core.logging import has_log

from lewis_emulators.tti355.device import SimulatedTti355


@has_log
class SimulatedTTIEX355P(SimulatedTti355):
    def _initialize_data(self):
        super()._initialize_data()
        self.min_voltage = 0.0
        self.min_current = 0.01

    def reset_ttiex355p(self):
        self._initialize_data()

    def voltage_within_limits(self, voltage):
        return self.min_voltage <= voltage and super().voltage_within_limits(voltage)

    def currrent_within_limits(self, current):
        return self.min_current <= current and super().current_within_limits(current)
