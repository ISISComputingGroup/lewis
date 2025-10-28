from .ethernet_device import EthernetDevice
from .utilities import format_int


class HmiDevice(EthernetDevice):
    OK_STATUS = "OK"

    def __init__(self, ip):
        self._status = HmiDevice.OK_STATUS
        self._base_page = 34
        self._sub_page = 2
        self._count_cycles = [
            "999",
            "006",
            "002",
            "002",
            "002",
            "002",
            "002",
            "002",
            "001",
            "001",
            "310",
        ]
        self._count = 0
        self._max_grabbed = 38
        self._limit = 20
        super(HmiDevice, self).__init__(ip)

    def base_page(self, as_string, length):
        return format_int(self._base_page, as_string, length)

    def sub_page(self, as_string, length):
        return format_int(self._sub_page, as_string, length)

    def count_cycles(self):
        return list(self._count_cycles)

    def max_grabbed(self, as_string, length):
        return format_int(self._max_grabbed, as_string, length)

    def limit(self, as_string, length):
        return format_int(self._limit, as_string, length)

    def count(self, as_string, length):
        return format_int(self._count, as_string, length)

    def status(self):
        return self._status
