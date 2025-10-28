class EthernetDevice(object):
    """An ethernet device that the rig communicates with."""

    def __init__(self, ip):
        assert type(ip) is str
        self._ip = ip

    def ip(self):
        return self._ip
