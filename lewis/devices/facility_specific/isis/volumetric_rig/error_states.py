class ErrorStates(object):
    """The possible error states the device can be in."""

    def __init__(self):
        self.run = False
        self.hmi = False
        self.gauges = False
        self.comms = False
        self.estop = False
