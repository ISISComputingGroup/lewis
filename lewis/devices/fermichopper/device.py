from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState, GoingState, StoppedState, StoppingState


class SimulatedFermichopper(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self.last_command = "0000"
        self.speed = 0
        self.speed_setpoint = 0
        self._allowed_speed_setpoints = list(50 * i for i in range(1, 13))

        self.delay_highword = 0
        self.delay_lowword = 0
        self.delay = 0

        self.gatewidth = 0

        self.electronics_temp = 30.0
        self.motor_temp = 30.0

        self.voltage = 0
        self.current = 0

        self.autozero_1_lower = 0
        self.autozero_2_lower = 0
        self.autozero_1_upper = 0
        self.autozero_2_upper = 0

        self.drive = False
        self.runmode = False
        self.magneticbearing = False

        self.parameters = None

        self.is_lying_about_delay_sp_rbv = False
        self.is_lying_about_gatewidth = False
        self.is_broken = False

    def reset(self):
        self._initialize_data()

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
            "stopping": StoppingState(),
            "going": GoingState(),
            "stopped": StoppedState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("default", "stopped"), lambda: not self.runmode),
                (("default", "going"), lambda: self.runmode),
                (("stopped", "going"), lambda: self.runmode),
                (("going", "stopping"), lambda: self.runmode is False),
                (("stopping", "stopped"), lambda: self.speed == 0),
            ]
        )

    def do_command(self, command):
        valid_commands = ["0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008"]
        assert command in valid_commands, "Invalid command."

        self.last_command = command

        if command == "0001":
            self.drive = True
            self.runmode = False
        elif command == "0002":
            self.drive = False
        elif command == "0003":
            if self.drive and self.speed_setpoint == 600:
                self.is_broken = True
            self.drive = True
            self.runmode = True
        elif command == "0004":
            self.magneticbearing = True
        elif command == "0005":
            self.magneticbearing = False
        elif command == "0006":
            self.parameters = ChopperParameters.MERLIN_LARGE
        elif command == "0007":
            self.parameters = ChopperParameters.HET_MARI
        elif command == "0008":
            self.parameters = ChopperParameters.MERLIN_SMALL

    def get_last_command(self):
        return self.last_command

    def set_speed_setpoint(self, value):
        assert value in self._allowed_speed_setpoints, "Speed setpoint {} not allowed".format(value)

        if value == 600 and self.speed_setpoint == 600 and self.speed == 600:
            self.is_broken = True

        self.speed_setpoint = value

    def get_speed_setpoint(self):
        return self.speed_setpoint

    def set_true_speed(self, value):
        self.speed = value

    def get_true_speed(self):
        return self.speed

    def set_delay_highword(self, value):
        self.delay_highword = value
        self.update_delay()

    def set_delay_lowword(self, value):
        self.delay_lowword = value
        self.update_delay()

    def update_delay(self):
        self.delay = self.delay_highword * 65536 + self.delay_lowword
        self.is_lying_about_delay_sp_rbv = (
            False  # Resending the setpoint causes the device to no longer be confused
        )

    def set_gate_width(self, value):
        self.gatewidth = value
        self.is_lying_about_gatewidth = (
            False  # Resending the setpoint causes the device to no longer be confused
        )

    def get_gate_width(self):
        if self.is_lying_about_gatewidth:
            return self.gatewidth + 123
        else:
            return self.gatewidth

    def get_electronics_temp(self):
        return self.electronics_temp

    def get_motor_temp(self):
        return self.motor_temp

    def get_voltage(self):
        return self.voltage

    def get_current(self):
        return self.current

    def get_nominal_delay(self):
        if self.is_lying_about_delay_sp_rbv:
            return self.delay + 123
        else:
            return self.delay

    def get_actual_delay(self):
        return self.delay


class ChopperParameters(object):
    MERLIN_SMALL = 1
    MERLIN_LARGE = 2
    HET_MARI = 3
