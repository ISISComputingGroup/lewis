from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .buffer import Buffer
from .error_states import ErrorStates
from .ethernet_device import EthernetDevice
from .gas import Gas
from .hmi_device import HmiDevice
from .pressure_sensor import PressureSensor
from .seed_gas_data import SeedGasData
from .sensor import Sensor
from .states import DefaultInitState, DefaultRunningState
from .system_gases import SystemGases
from .two_gas_mixer import TwoGasMixer
from .utilities import format_float, format_int
from .valve import Valve


class SimulatedVolumetricRig(StateMachineDevice):
    HALTED_MESSAGE = "Rejected only allowed when running"

    def _initialize_data(self):
        # Device modes
        self.serial_command_mode = True
        self._cycle_pressures = False

        # Set up all available gases
        self._system_gases = SystemGases(
            [Gas(i, SeedGasData.names[i]) for i in range(len(SeedGasData.names))]
        )

        # Set mixable gases
        self._mixer = TwoGasMixer()
        for name1, name2 in SeedGasData.mixable_gas_names():
            self._mixer.add_mixable(
                self._system_gases.gas_by_name(name1),
                self._system_gases.gas_by_name(name2),
            )

        # Set buffers
        buffer_gases = [
            (
                self._system_gases.gas_by_name(name1),
                self._system_gases.gas_by_name(name2),
            )
            for name1, name2 in SeedGasData.buffer_gas_names()
        ]
        self._buffers = [
            Buffer(i + 1, buffer_gases[i][0], buffer_gases[i][1])
            for i in range(len(buffer_gases))
        ]

        # Set ethernet devices
        self._plc = EthernetDevice("192.168.0.1")
        self._hmi = HmiDevice("192.168.0.2")

        # Target pressure: We can't set this via serial
        self._target_pressure = 100.00

        # Set up sensors
        self._temperature_sensors = [Sensor() for _ in range(9)]
        self._pressure_sensors = [PressureSensor() for _ in range(5)]

        # Set up special valves
        self._supply_valve = Valve()
        self._vacuum_extract_valve = Valve()
        self._cell_valve = Valve()

        # Misc system state variables
        self._halted = False
        self._status_code = 2
        self._errors = ErrorStates()

    def _get_state_handlers(self):
        return {
            "init": DefaultInitState(),
            "running": DefaultRunningState(),
        }

    def _get_initial_state(self):
        return "init"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("init", "running"), lambda: self.serial_command_mode),
            ]
        )

    def identify(self):
        return "ISIS Volumetric Gas Handing Panel"

    def buffer_count(self):
        return len(self._buffers)

    def buffer(self, i):
        try:
            return next(b for b in self._buffers if b.index() == i)
        except StopIteration:
            return None

    def memory_location(self, location, as_string, length):
        # Currently returns the value at the location as the location itself.
        return format_int(location, as_string, length)

    def plc(self):
        return self._plc

    def hmi(self):
        return self._hmi

    def halted(self):
        return self._halted

    def halt(self):
        self._halted = True

    def pressure_sensors(self, reverse=False):
        return (
            self._pressure_sensors
            if not reverse
            else list(reversed(self._pressure_sensors))
        )

    def temperature_sensors(self, reverse=False):
        return (
            self._temperature_sensors
            if not reverse
            else list(reversed(self._temperature_sensors))
        )

    def target_pressure(self, as_string):
        return format_float(self._target_pressure, as_string)

    def status_code(self, as_string=False, length=None):
        # We don't currently do any logic for the system status, it always returns 2
        return format_int(2, as_string, length)

    def errors(self):
        return self._errors

    def valve_count(self):
        return len(self.valves_status())

    def valves_status(self):
        # The valve order goes: supply, vacuum, cell, buffer(n), ... , buffer(1)
        return [
            self._supply_valve.status(),
            self._vacuum_extract_valve.status(),
            self._cell_valve.status(),
        ] + [b.valve_status() for b in list(reversed(self._buffers))]

    def buffer_valve_is_open(self, buffer_number):
        buff = self.buffer(buffer_number)
        return buff.valve_is_open() if buff is not None else False

    def vacuum_valve_is_open(self):
        return self._vacuum_extract_valve.is_open()

    def cell_valve_is_open(self):
        return self._cell_valve.is_open()

    def buffer_valve_is_enabled(self, buffer_number):
        buff = self.buffer(buffer_number)
        return buff.valve_is_enabled() if buff is not None else False

    def vacuum_valve_is_enabled(self):
        return self._vacuum_extract_valve.is_enabled()

    def cell_valve_is_enabled(self):
        return self._cell_valve.is_enabled()

    def open_buffer_valve(self, buffer_number):
        if not self._halted:
            buff = self.buffer(buffer_number)
            # The buffer must exist and the system gas connected to it must be mixable with all the other current
            # buffer gases
            if buff is not None and all(
                self._mixer.can_mix(buff.system_gas(), b.buffer_gas())
                for b in self._buffers
            ):
                buff.open_valve(self._mixer)

    def open_cell_valve(self):
        if not self._halted:
            self._cell_valve.open()

    def open_vacuum_valve(self):
        if not self._halted:
            # We can't open the vacuum valve if any of the buffer valves are open
            if not any([b.valve_is_open() for b in self._buffers]):
                self._vacuum_extract_valve.open()

    def close_buffer_valve(self, buffer_number):
        if not self._halted:
            buff = self.buffer(buffer_number)
            if buff is not None:
                buff.close_valve()

    def close_cell_valve(self):
        if not self._halted:
            self._cell_valve.close()

    def close_vacuum_valve(self):
        if not self._halted:
            self._vacuum_extract_valve.close()

    def enable_cell_valve(self):
        if not self._halted:
            self._cell_valve.enable()

    def enable_vacuum_valve(self):
        if not self._halted:
            self._vacuum_extract_valve.enable()

    def enable_buffer_valve(self, buffer_number):
        if not self._halted:
            buff = self.buffer(buffer_number)
            if buff is not None:
                buff.enable_valve()

    def disable_cell_valve(self):
        if not self._halted:
            self._cell_valve.disable()

    def disable_vacuum_valve(self):
        if not self._halted:
            self._vacuum_extract_valve.disable()

    def disable_buffer_valve(self, buffer_number):
        if not self._halted:
            buff = self.buffer(buffer_number)
            if buff is not None:
                buff.disable_valve()

    def buffers(self):
        return self._buffers

    def mixer(self):
        return self._mixer

    def update_pressures(self, dt):
        # This is a custom behaviour designed to cycle through various valve behaviours. It will ramp up the pressure
        # to the maximum, close and disable all valves, then let the pressure drop and enable and subsequently reopen
        # the valves
        if self._cycle_pressures:
            number_of_open_buffers = sum(1 for b in self._buffers if b.valve_is_open())
            for p in self._pressure_sensors:
                base_rate = 10.0
                if number_of_open_buffers > 0:
                    # Approach a pressure above target pressure so we intentionally go over the limit
                    from random import random

                    p.approach_value(
                        dt,
                        1.1 * self._target_pressure,
                        base_rate
                        * float(number_of_open_buffers)
                        / self.buffer_count()
                        * random(),
                    )
                else:
                    p.approach_value(dt, 0.0, base_rate)
                if self._overall_pressure() < 0.5 * self._target_pressure:
                    for b in self._buffers:
                        b.enable_valve()
                        if self._overall_pressure() < 0.1 * self._target_pressure:
                            b.open_valve(self._mixer)

        # Check if system pressure is over the maximum and disable valves if necessary
        self._check_pressure()

    def _overall_pressure(self):
        # This calculates the pressure based on the 5 readings from the pressure sensor. At the moment this is done in
        # an ad hoc fashion. The actual behaviour hasn't been set on the real device, and it is likely the output from
        # the PMV command could change in the future to give the actual reference pressure.
        return max(s.value() for s in self._pressure_sensors)

    def _check_pressure(self):
        # Disable the buffer valves if the pressure exceeds the limit
        if self._overall_pressure() > self._target_pressure:
            for b in self._buffers:
                b.disable_valve()

    def cycle_pressures(self, on):
        # Switch on/off pressure cycling
        self._cycle_pressures = on

    def set_pressures(self, value):
        # Sets all pressure sensors to have the same value
        for p in self._pressure_sensors:
            p.set_value(value, self._target_pressure)

    def set_pressure_target(self, value):
        self._target_pressure = value

    def system_gases(self):
        return self._system_gases
