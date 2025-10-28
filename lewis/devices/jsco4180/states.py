from lewis.core.statemachine import State


class PumpOff(State):
    def on_entry(self, dt):
        device = self._context
        device.flowrate = 0.0
        device.pressure = 0.0


class PumpOn(State):
    def on_entry(self, dt):
        device = self._context
        device.simulate_pumping()


class PumpProgram(State):
    def on_entry(self, dt):
        device = self._context
        device.simulate_pumping()


class PumpProgramReset(State):
    def on_entry(self, dt):
        device = self._context
        device.simulate_pumping()
