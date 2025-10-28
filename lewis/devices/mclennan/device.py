from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import HomingState, JoggingState, MovingState, StoppedState

states = OrderedDict(
    [
        ("Stopped", StoppedState()),
        ("Moving", MovingState()),
        ("Homing", HomingState()),
        ("Jogging", JoggingState()),
    ]
)


class SimulatedMclennan(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.connected = True
        self.is_jogging = False
        self.is_moving = False
        self.is_homing = False
        self.is_pm304 = False
        self.has_sent_BA = False
        self.is_idle = True
        self.jog_velocity = 0
        self.position = 0
        self.target_position = 0
        self.current_op = "Idle"
        self.creep_speed1 = 700
        self.creep_speed2 = 700
        self.creep_speed3 = 700
        self.creep_speedz = 700

        self.velocity = {}
        self.creep_speed = {}
        self.accl = {}
        self.decl = {}
        self.mode = {}
        self.encoder_ratio = {}
        self.window = {}
        self.timeout = {}
        self.tracking_window = {}
        self.enable_limits = {}
        self.backoff = {}
        self.creep_steps = {}
        self.settle_time = {}
        self.abort_mode = {}
        self.datum_mode = {}
        self.home_pos = {}
        for i in range(1, 10):
            self.velocity[i] = 0
            self.creep_speed[i] = 700
            self.accl[i] = 1000
            self.decl[i] = 1000
            self.mode[i] = 1
            self.encoder_ratio[i] = 1.0
            self.window[i] = 10
            self.timeout[i] = 400
            self.tracking_window[i] = 300
            self.enable_limits[i] = False
            self.backoff[i] = 0
            self.creep_steps[i] = 10
            self.settle_time[i] = 1000
            self.abort_mode[i] = "00000000"
            self.datum_mode[i] = "00000000"
            self.home_pos[i] = 0

    def jog(self, velocity):
        self.jog_velocity = velocity
        self.is_jogging = True

    def home(self):
        self.is_homing = True

    def moveAbs(self, controller, pos):
        self.target_position = pos
        self.jog_velocity = self.velocity[controller]
        self.is_moving = True

    def moveRel(self, controller, pos):
        self.target_position = self.position + pos
        self.jog_velocity = self.velocity[controller]
        self.is_moving = True

    def stop(self):
        self.is_jogging = False
        self.is_moving = False
        self.is_homing = False
        self.is_idle = True
        self.current_op = "Idle"

    def _get_state_handlers(self):
        return states

    def _get_initial_state(self):
        return "Stopped"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("Stopped", "Jogging"), lambda: self.is_jogging),
                (("Jogging", "Stopped"), lambda: not self.is_jogging),
                (("Stopped", "Moving"), lambda: self.is_moving),
                (("Moving", "Stopped"), lambda: not self.is_moving),
                (("Stopped", "Homing"), lambda: self.is_homing),
                (("Homing", "Stopped"), lambda: not self.is_homing),
            ]
        )
