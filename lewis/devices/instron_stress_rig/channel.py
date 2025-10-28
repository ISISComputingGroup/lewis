class Channel(object):
    def __init__(self):
        self.waveform_type = 0
        self.step_time = 0
        self.ramp_amplitude_setpoint = 0
        self.scale = 10
        self.value = 0
        self.transducer_type = 0


class PositionChannel(Channel):
    def __init__(self):
        super(PositionChannel, self).__init__()
        self.channel_type = 3


class StressChannel(Channel):
    def __init__(self):
        super(StressChannel, self).__init__()
        self.area = 1
        self.channel_type = 2


class StrainChannel(Channel):
    def __init__(self):
        super(StrainChannel, self).__init__()
        self.length = 1
        self.channel_type = 4
