from collections import OrderedDict
from enum import Enum

from lewis.devices import StateMachineDevice

from .states import DefaultState


class OnOffStates(Enum):
    """Holds whether a device function is on or off"""

    on = 4
    off = 0


class PumpStates(object):
    """The pump states"""

    stopped = object()
    starting_delay = object()
    accelerating = object()
    running = object()
    stopping_short_delay = object()
    stopping_normal_delay = object()
    fault_braking = object()
    braking = object()


class GaugeStates(object):
    """Possible gauge states"""

    not_connected = object()
    connected = object()
    new_id = object()
    change = object()
    alert = object()
    off = object()
    striking = object()
    initialising = object()
    calibrating = object()
    zeroing = object()
    degassing = object()
    on = object()
    inhibited = object()


class PriorityStates(object):
    """Priority values"""

    OK = object()
    Warning = object()
    Alarm = object()


class GaugeUnits(object):
    """Units the gauges can measure in"""

    Pa = object()
    V = object()
    percent = object()


class SimulatedEdwardsTIC(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self._turbo_pump = PumpStates.stopped
        self._turbo_priority = PriorityStates.OK
        self._turbo_alert = 0
        self._turbo_in_standby = False

        self._gauge_state = GaugeStates.on
        self._gauge_priority = PriorityStates.OK
        self._gauge_alert = 0
        self._gauge_pressure = 0.0
        self._gauge_units = GaugeUnits.Pa

        self.connected = True

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    @property
    def turbo_in_standby(self):
        """Gets whether the turbo is in standby mode

        Returns:
            _turbo_standby: Bool, True if the turbo is in standby mode
        """
        return self._turbo_in_standby

    @turbo_in_standby.setter
    def turbo_in_standby(self, value):
        """Sets the turbo standby mode

        Args:
            value: Bool, True to set standby mode. False to unset standby mode
        """
        self._turbo_in_standby = value

    def turbo_set_standby(self, value):
        """Sets / unsets turbo standby mode

        Args:
            value, int: 1 to set standby mode, 0 to unset standby.
        """
        if value == 1:
            self.log.info("Entering turbo standby mode")
            self._turbo_in_standby = True
        elif value == 0:
            self.log.info("Leaving turbo standby mode")
            self._turbo_in_standby = False
        else:
            raise ValueError("Invalid standby argument provided ({} not 0 or 1)".format(value))

    @property
    def turbo_pump(self):
        """Gets the running state of the turbo pump"""
        return self._turbo_pump

    def set_turbo_pump_state(self, state):
        """Sets the state of the turbo pump.
        This function doesn't exist on the real device and is only called through the back door.

        Args:
            state: String, Matches an attribute of the PumpStates class
        """
        pump_state = getattr(PumpStates, state)

        self._turbo_pump = pump_state

    def turbo_start_stop(self, value):
        """Sets the turbo pump running/stopping

        Args:
            value: int, 1 if starting the pump 0 to stop the pump
        """
        self.log.info("Starting or stopping turbo {}".format(value))

        if value == 1:
            self.log.info("Starting turbo")
            self._turbo_pump = PumpStates.running
        elif value == 0:
            self.log.info("Stopping turbo")
            self._turbo_pump = PumpStates.stopped
        else:
            raise ValueError("Invalid start/stop switch ({} not 0 or 1)".format(value))

    @property
    def turbo_priority(self):
        """Gets the priority state of the turbo pump"""
        self.log.info("Getting priority {}".format(self._turbo_priority))

        return self._turbo_priority

    def set_turbo_priority(self, state):
        """Sets the priority state of the turbo pump.
        This function doesn't exist on the real device and is only called through the back door.

        Args:
            state: object, an attribute of the PumpStates class
        """
        priority_state = getattr(PriorityStates, state)

        self._turbo_priority = priority_state

    @property
    def turbo_alert(self):
        """Gets the alert state of the turbo pump"""
        return self._turbo_alert

    # This setter doesn't exist on the 'real' device
    def set_turbo_alert(self, state):
        """Sets the alert state of the turbo pump

        Args:
            state: Int, the alert value
        """
        self._turbo_alert = state

    @property
    def gauge_pressure(self):
        """Gets the gauge pressure"""
        return self._gauge_pressure

    @gauge_pressure.setter
    def gauge_pressure(self, value):
        """Sets the gauge pressure.
        This function is not present on the real device and can only be accessed through the backdoor.

        Args:
            value: float, The value to set the gauge pressure to.
        """
        self._gauge_pressure = value

    @property
    def gauge_state(self):
        """Gets the running state of the gauges"""
        return self._gauge_state

    def set_gauge_state(self, state):
        """Sets the state of the gauges
        This function doesn't exist on the real device and is only called through the back door.

        Args:
            state: String, Matches an attribute of the GaugeStates class
        """
        gauge_state = getattr(GaugeStates, state)

        self._gauge_state = gauge_state

    @property
    def gauge_alert(self):
        return self._gauge_alert

    def set_gauge_alert(self, state):
        """Sets the alert state of the gauges.
        This is only accessed through the back door

        Args:
            state: Int, the alert value
        """
        self._gauge_alert = state

    @property
    def gauge_priority(self):
        """Gets the priority state of the gauges"""
        return self._gauge_priority

    def set_gauge_priority(self, state):
        """Sets the priority state of the gauges.
        This function doesn't exist on the real device and is only called through the back door.

        Args:
            state: object, an attribute of the PumpStates class
        """
        priority_state = getattr(PriorityStates, state)

        self._gauge_priority = priority_state

    @property
    def gauge_units(self):
        """Getter for the gauge units"""
        return self._gauge_units
