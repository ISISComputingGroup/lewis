from collections import OrderedDict

from lewis.devices.ips.modes import Activity, Control, Mode, SweepMode

from lewis.core.logging import has_log
from lewis.devices import StateMachineDevice

from .states import HeaterOffState, HeaterOnState, MagnetQuenchedState

# As long as no magnetic saturation effects are present, there is a linear relationship between Teslas and Amps.
#
# This is called the load line. For more detailed (technical) discussion about the load line see:
# - http://aries.ucsd.edu/LIB/REPORT/SPPS/FINAL/chap4.pdf (section 4.3.3)
# - http://www.prizz.fi/sites/default/files/tiedostot/linkki1ID346.pdf (slide 11)
LOAD_LINE_GRADIENT = 0.01


def amps_to_tesla(amps):
    return amps * LOAD_LINE_GRADIENT


def tesla_to_amps(tesla):
    return tesla / LOAD_LINE_GRADIENT


@has_log
class SimulatedIps(StateMachineDevice):
    # Currents that correspond to the switch heater being on and off
    HEATER_OFF_CURRENT, HEATER_ON_CURRENT = 0, 10

    # If there is a difference in current of more than this between the magnet and the power supply, and the switch is
    # resistive, then the magnet will quench.
    # No idea what this number should be for a physically realistic system so just guess.
    QUENCH_CURRENT_DELTA = 0.1

    # Maximum rate at which the magnet can safely ramp without quenching.
    MAGNET_RAMP_RATE = 1000

    # Fixed rate at which switch heater can ramp up or down
    HEATER_RAMP_RATE = 5

    def _initialize_data(self):
        """Initialize all of the device's attributes."""
        self.reset()

    def reset(self):
        # Within the cryostat, there is a wire that is made superconducting because it is in the cryostat. The wire has
        # a heater which can be used to make the wire go back to a non-superconducting state.
        #
        # When the heater is ON, the wire has a high resistance and the magnet is powered directly by the power supply.
        #
        # When the heater is OFF, the wire is superconducting, which means that the power supply can be ramped down and
        # the magnet will stay active (this is "persistent" mode)
        self.heater_on = False
        self.heater_current = 0

        # "Leads" are the non-superconducting wires between the superconducting magnet and the power supply.
        # Not sure what a realistic value is for these leads, so I've guessed.
        self.lead_resistance = 50

        # Current = what the power supply is providing.
        self.current = 0
        self.current_setpoint = 0

        # Current for the magnet. May be different from the power supply current if the magnet is in persistent mode.
        self.magnet_current = 0

        # Measured current may be different from what the PSU is attempting to provide
        self.measured_current = 0

        # If the device trips, store the last current which caused a trip in here.
        # This could be used for diagnostics e.g. finding maximum field which magnet is capable of in a certain config.
        self.trip_current = 0

        # Ramp rate == sweep rate
        self.current_ramp_rate = 1 / LOAD_LINE_GRADIENT

        # Set to true if the magnet is quenched - this will cause lewis to enter the quenched state
        self.quenched = False

        # Mode of the magnet e.g. HOLD, TO SET POINT, TO ZERO, CLAMP
        self.activity = Activity.TO_SETPOINT

        # No idea what a sensible value is. Hard-code this here for now - can't be changed on real device.
        self.inductance = 0.005

        # No idea what sensible values are here. Also not clear what the behaviour is of the controller when these
        # limits are hit.
        self.neg_current_limit, self.pos_current_limit = -(10**6), 10**6

        # Local and locked is the zeroth mode of the control command
        self.control = Control.LOCAL_LOCKED

        # The only sweep mode we are interested in is tesla fast
        self.sweep_mode = SweepMode.TESLA_FAST

        # Not sure what is the sensible value here
        self.mode = Mode.SLOW

    def _get_state_handlers(self):
        return {
            "heater_off": HeaterOffState(),
            "heater_on": HeaterOnState(),
            "quenched": MagnetQuenchedState(),
        }

    def _get_initial_state(self):
        return "heater_off"

    def _get_transition_handlers(self):
        return OrderedDict(
            [
                (("heater_off", "heater_on"), lambda: self.heater_on),
                (("heater_on", "heater_off"), lambda: not self.heater_on),
                (("heater_on", "quenched"), lambda: self.quenched),
                (("heater_off", "quenched"), lambda: self.quenched),
                # Only triggered when device is reset or similar
                (
                    ("quenched", "heater_off"),
                    lambda: not self.quenched and not self.heater_on,
                ),
                (
                    ("quenched", "heater_on"),
                    lambda: not self.quenched and self.heater_on,
                ),
            ]
        )

    def quench(self, reason):
        self.log.info(
            "Magnet quenching at current={} because: {}".format(self.current, reason)
        )
        self.trip_current = self.current
        self.magnet_current = 0
        self.current = 0
        self.measured_current = 0
        self.quenched = True  # Causes LeWiS to enter Quenched state

    def unquench(self):
        self.quenched = False

    def get_voltage(self):
        """Gets the voltage of the PSU.

        Everything except the leads is superconducting, we use Ohm's law here with the PSU current and the lead
        resistance.

        In reality would also need to account for inductance effects from the magnet but I don't think that
        extra complexity is necessary for this emulator.
        """
        return self.current * self.lead_resistance

    def set_heater_status(self, new_status):
        if (
            new_status
            and abs(self.current - self.magnet_current) > self.QUENCH_CURRENT_DELTA
        ):
            raise ValueError(
                "Can't set the heater to on while the magnet current and PSU current are mismatched"
            )
        self.heater_on = new_status
