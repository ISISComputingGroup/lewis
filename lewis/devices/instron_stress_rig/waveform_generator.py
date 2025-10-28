import math
from datetime import datetime, timedelta

from .quarter_cycle_event_detector import QuarterCycleEventDetector as QCED
from .waveform_generator_states import WaveformGeneratorStates as GenStates
from .waveform_types import WaveformTypes


class WaveformGenerator(object):
    STOP_DELAY = timedelta(seconds=3)

    def __init__(self):
        self.state = GenStates.STOPPED
        self.amplitude = {i + 1: 0.0 for i in range(3)}
        self.frequency = {i + 1: 1.0 for i in range(3)}
        self.type = {i + 1: WaveformTypes.SINE for i in range(3)}
        self.stop_requested_at_time = None
        self.quart_counter = QCED()

    def abort(self):
        if self.active():
            self.state = GenStates.ABORTED
            self.stop_requested_at_time = None
            self.quart_counter.off()

    def finish(self):
        if self.active():
            self.stop_requested_at_time = datetime.now()
            self.state = GenStates.FINISHING

    def time_to_stop(self):
        return (
            self.stop_requested_at_time is not None
            and (datetime.now() - self.stop_requested_at_time) > WaveformGenerator.STOP_DELAY
        )

    def stop(self):
        self.stop_requested_at_time = None
        self.state = GenStates.STOPPED
        self.quart_counter.off()

    def start(self):
        self.state = GenStates.RUNNING
        self.stop_requested_at_time = None

    def hold(self):
        if self.active():
            self.state = GenStates.HOLDING

    def maintain_log(self):
        # Does nothing in current emulator
        pass

    def active(self):
        return self.state in [GenStates.RUNNING, GenStates.HOLDING]

    def get_value(self, channel):
        def sin(a, x, f):
            return a * math.sin(math.pi * x * f)

        def square(a, x, f):
            return math.copysign(a, sin(a, x, f))

        def sawtooth(a, x, f):
            return a * (x % (1.0 / f))

        def triangle(a, x, f):
            return a * (1 - 2 * abs((f * x - 0.5) % 2 - 1))

        def haversine(a, x, f):
            return a / 2.0 * (1.0 - math.cos(math.pi * f * x))

        def havertriangle(a, x, f):
            return a * (1 - abs(f * x % 2 - 1))

        def haversquare(a, x, f):
            return a / 2.0 * (1.0 + math.copysign(1.0, haversine(a, x, f) - 0.5))

        if self.active():
            amp = self.amplitude[channel]
            freq = max(self.frequency[channel], 1.0e-20)
            wave_type = self.type[channel]
            val = self.quart_counter.counts

            if not self.active():
                return 0.0
            elif wave_type == WaveformTypes.TRIANGLE:
                return triangle(amp, val, freq)
            elif wave_type == WaveformTypes.SAWTOOTH:
                return sawtooth(amp, val, freq)
            elif wave_type == WaveformTypes.SQUARE:
                return square(amp, val, freq)
            elif wave_type == WaveformTypes.HAVERSINE:
                return haversine(amp, val, freq)
            elif wave_type == WaveformTypes.HAVERSQUARE:
                return haversquare(amp, val, freq)
            elif wave_type == WaveformTypes.HAVERTRIANGLE:
                return havertriangle(amp, val, freq)
            else:
                return sin(amp, val, freq)

        return 0.0
