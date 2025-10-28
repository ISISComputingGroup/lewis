from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from ..device import GaugeStates, GaugeUnits, PriorityStates, PumpStates

PUMPSTATES_MAP = {
    0: PumpStates.stopped,
    1: PumpStates.starting_delay,
    5: PumpStates.accelerating,
    4: PumpStates.running,
    2: PumpStates.stopping_short_delay,
    3: PumpStates.stopping_normal_delay,
    6: PumpStates.fault_braking,
    7: PumpStates.braking,
}

GAUGESTATES_MAP = {
    0: GaugeStates.not_connected,
    1: GaugeStates.connected,
    2: GaugeStates.new_id,
    3: GaugeStates.change,
    4: GaugeStates.alert,
    5: GaugeStates.off,
    6: GaugeStates.striking,
    7: GaugeStates.initialising,
    8: GaugeStates.calibrating,
    9: GaugeStates.zeroing,
    10: GaugeStates.degassing,
    11: GaugeStates.on,
    12: GaugeStates.inhibited,
}

GAUGEUNITS_MAP = {GaugeUnits.Pa: 59, GaugeUnits.V: 66, GaugeUnits.percent: 81}

PRIORITYSTATES_MAP = {
    PriorityStates.OK: 0,
    PriorityStates.Warning: 1,
    PriorityStates.Alarm: 3,
}


def reverse_dict_lookup(dictionary, value_to_find):
    """Looks up the key for the supplied value in dictionary dict.

    Args:
        dictionary: dictionary, the dictionary to do the reverse lookup
        value_to_find: the value to find in the dictionary

    Raises:
        KeyError if value does not exist in the dictionary
    """
    for key, value in dictionary.items():
        if value == value_to_find:
            return key
    else:
        raise KeyError("Could not find {} in map".format(value_to_find))


@has_log
class EdwardsTICStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("turbo_start_stop").escape("!C904 ").int().eos().build(),
        CmdBuilder("get_turbo_state").escape("?V904").eos().build(),
        CmdBuilder("turbo_get_speed").escape("?V905").eos().build(),
        CmdBuilder("turbo_get_sft").escape("?S905").eos().build(),
        CmdBuilder("turbo_get_power").escape("?V906").eos().build(),
        CmdBuilder("turbo_get_norm").escape("?V907").eos().build(),
        CmdBuilder("turbo_set_standby").escape("!C908 ").int().eos().build(),
        CmdBuilder("turbo_get_standby").escape("?V908").eos().build(),
        CmdBuilder("turbo_get_cycle").escape("?V909").eos().build(),
        CmdBuilder("backing_get_status").escape("?V910").eos().build(),
        CmdBuilder("backing_start_stop").escape("!C910 ").int().eos().build(),
        CmdBuilder("backing_get_speed").escape("?V911").eos().build(),
        CmdBuilder("backing_get_power").escape("?V912").eos().build(),
        CmdBuilder("get_gauge").escape("?V91").arg("3|4|5").eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    ACK = "&ACK!" + out_terminator

    def handle_error(self, request, error):
        """Prints an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.

        Returns:
            None.
        """
        self.log.info("An error occurred at request {}: {}".format(request, error))

    @conditional_reply("connected")
    def turbo_set_standby(self, switch):
        self._device.turbo_set_standby(switch)

        return "*C908 0"

    @conditional_reply("connected")
    def turbo_get_standby(self):
        return_string = "=V908 {stdby_state};0;0"

        standby_state = 4 if self._device.turbo_in_standby else 0

        self.log.info(return_string.format(stdby_state=standby_state))

        return return_string.format(stdby_state=standby_state)

    @conditional_reply("connected")
    def turbo_start_stop(self, switch):
        self.log.info("turbo start stop command received")
        self._device.turbo_start_stop(switch)

        return "*C904 0"

    @conditional_reply("connected")
    def get_turbo_state(self):
        state_string = "=V904 {turbo_state};{alert};{priority}"

        return state_string.format(
            turbo_state=reverse_dict_lookup(PUMPSTATES_MAP, self._device.turbo_pump),
            alert=self._device.turbo_alert,
            priority=PRIORITYSTATES_MAP[self._device.turbo_priority],
        )

    @conditional_reply("connected")
    def get_turbo_status(self):
        output_string = "*C904 {state};{alert};{priority}"

        state = self._device.turbo_state
        alert = self._device.turbo_alert
        priority = self._device.turbo_priority

        return output_string.format(state=state, alert=alert, priority=priority)

    @conditional_reply("connected")
    def turbo_get_speed(self):
        return "=V905 1;0;0"

    @conditional_reply("connected")
    def turbo_get_sft(self):
        return "=S905 1;0"

    @conditional_reply("connected")
    def turbo_get_power(self):
        return "=V906 1;0;0"

    @conditional_reply("connected")
    def turbo_get_norm(self):
        return "=V907 4;0;0"

    @conditional_reply("connected")
    def turbo_get_cycle(self):
        return "=V909 1;0;0;0"

    @conditional_reply("connected")
    def backing_get_status(self):
        return "=V910 1;0;0"

    @conditional_reply("connected")
    def backing_start_stop(self, switch):
        return "*C910 0"

    @conditional_reply("connected")
    def backing_get_speed(self):
        return "=V911 1;0;0"

    @conditional_reply("connected")
    def backing_get_power(self):
        return "=V912 1;0;0"

    @conditional_reply("connected")
    def get_gauge(self, gauge_id):
        state_string = (
            "=V91{gauge_id} {pressure};{units};{gauge_state};{alert};{priority}"
        )

        return state_string.format(
            gauge_id=gauge_id,
            pressure=self._device.gauge_pressure,
            units=GAUGEUNITS_MAP[self._device.gauge_units],
            gauge_state=reverse_dict_lookup(GAUGESTATES_MAP, self._device.gauge_state),
            alert=self._device.gauge_alert,
            priority=PRIORITYSTATES_MAP[self._device.gauge_priority],
        )
