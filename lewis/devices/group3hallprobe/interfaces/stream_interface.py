import logging

from lewis.devices.group3hallprobe.device import Ranges, SimulatedGroup3HallProbe

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

if_connected = conditional_reply("connected")


@has_log
class Group3HallProbeStreamInterface(StreamInterface):
    in_terminator = "\n\r"  # Yes, really LF-CR not CR-LF
    out_terminator = "\n\r"

    def __init__(self) -> None:
        super(Group3HallProbeStreamInterface, self).__init__()

        self.log: logging.Logger
        self.device: SimulatedGroup3HallProbe

        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.initialize)
            .escape("A")
            .int()
            .escape(" SE0GDR3GCNNUFG")
            .eos()
            .build(),
            CmdBuilder(self.get_field).escape("A").int().escape(" F").eos().build(),
            CmdBuilder(self.get_temperature)
            .escape("A")
            .int()
            .escape(" T")
            .eos()
            .build(),
            CmdBuilder(self.set_range)
            .escape("A")
            .int()
            .escape(" R")
            .int()
            .eos()
            .build(),
        }

    def handle_error(self, request: str, error: str | Exception) -> None:
        """
        If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error(
            "An error occurred at request " + repr(request) + ": " + repr(error)
        )

    @if_connected
    def initialize(self, probe_id: int) -> str:
        self.device.probes[probe_id].initialize()
        return f"A{probe_id} SE0GDR3GCNNUFG"

    @if_connected
    def get_field(self, probe_id: int) -> str:
        probe = self.device.probes[probe_id]
        if not probe.initialized:
            return f"A{probe_id} F\n\runinitialized_bad_data"
        if probe.is_over_range():
            return f"A{probe_id} F\n\rOVER RANGE"
        return f"A{probe_id} F\n\r{probe.field}"

    @if_connected
    def get_temperature(self, probe_id: int) -> str:
        probe = self.device.probes[probe_id]
        if not probe.initialized:
            return f"A{probe_id} T\n\runinitialized_bad_data"
        return f"A{probe_id} T\n\r{probe.temperature}C"

    @if_connected
    def set_range(self, probe_id: int, range_id: int) -> str:
        self.device.probes[probe_id].sensor_range = Ranges(range_id)
        return f"A{probe_id} R{range_id}"
