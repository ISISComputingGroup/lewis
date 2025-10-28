from enum import Enum


class Channel(object):
    def __init__(self, channel):
        self.channel = channel
        self.reading = 0
        self.reading_units = "VDC"
        self.close = False


class StatusRegister(object):
    def __init__(self):
        self.buffer_full = False
        self.measurement_summary_status = False
        self.number_of_times_reset_and_cleared = 0

    def reset_and_clear(self):
        self.buffer_full = False
        self.measurement_summary_status = False
        self.number_of_times_reset_and_cleared += 1


class ScanTrigger(Enum):
    IMM = 0
    HOLD = 1
    MAN = 2
    BUS = 3
    TLIN = 4
    EXT = 5
    TIM = 6


class ReadStatus(Enum):
    SINGLE = 0
    MULIT = 1
