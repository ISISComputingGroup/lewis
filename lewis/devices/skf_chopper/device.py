from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedSKFChopper(StateMachineDevice):
    """Simulated SKF chopper. Very basic and only provides frequency as a parameter for now
    to perform a basic check of modbus comms.
    """

    def _initialize_data(self):
        """Sets the initial state of the device.
        """
        self.connected = True

        self.freq = 40
        self.send_ok_transid = True

        self.v13_norm = 0
        self.w13_norm = 0
        self.v24_norm = 0
        self.w24_norm = 0
        self.z12_norm = 0
        self.v13_fsv = 0
        self.w13_fsv = 0
        self.v24_fsv = 0
        self.w24_fsv = 0
        self.z12_fsv = 0

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
