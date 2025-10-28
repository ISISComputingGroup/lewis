from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedHgl(StateMachineDevice):
    """Simulated AM Int2-L pressure transducer.
    """

    def _initialize_data(self):
        """Sets the initial state of the device.
        """
        self.level = 2.0
        self.verbosity = 0
        self.prefix = 1

    def _get_state_handlers(self):
        """Returns: states and their names
        """
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """Returns: the name of the initial state
        """
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """Returns: the state transitions
        """
        return OrderedDict()
