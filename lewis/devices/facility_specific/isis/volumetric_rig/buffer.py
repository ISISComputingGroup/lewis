from .two_gas_mixer import TwoGasMixer
from .utilities import format_int
from .valve import Valve


class Buffer(object):
    """A buffer contains a gas and is connected to a supply of a specific system gas via a valve. The system gas can be
    changed and the buffer fills from the system gas it is connected to. The valve can only be opened if mixing of
    the system and buffer gas are permitted
    """

    def __init__(self, index, buffer_gas, system_gas):
        assert buffer_gas is not None
        assert system_gas is not None
        self._buffer_gas = buffer_gas
        self._system_gas = system_gas
        self._index = index
        self._valve = Valve()

    def _disable_valve(self):
        self._valve.disable()

    def _enable_valve(self):
        self._valve.enable()

    def index(self, as_string=False, length=1):
        return format_int(self._index, as_string, length)

    def open_valve(self, mixer):
        """Try to open the valve between the buffer and system. Nothing will happen if the buffer and system gases are not
                allowed to mix.

        :param mixer: The details of which gases can be mixed
        """
        assert isinstance(mixer, TwoGasMixer)
        if mixer.can_mix(self._buffer_gas, self._system_gas):
            self._valve.open()

    def close_valve(self):
        self._valve.close()

    def enable_valve(self):
        self._valve.enable()

    def disable_valve(self):
        """Disable the valve. If the valve is open when this is requested then it will be automatically closed"""
        self._valve.close()
        self._valve.disable()

    def valve_is_open(self):
        return self._valve.is_open()

    def valve_is_enabled(self):
        return self._valve.is_enabled()

    def valve_status(self):
        return self._valve.status()

    def buffer_gas(self):
        return self._buffer_gas

    def system_gas(self):
        return self._system_gas

    def set_system_gas(self, gas):
        """Set a new system gas. This is only possible if the valve is closed.

        :param gas: The new system gas
        """
        if not self._valve.is_open():
            self._system_gas = gas
