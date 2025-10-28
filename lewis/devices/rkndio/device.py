from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState

NUMBER_OF_D_Is = 6
NUMBER_OF_D_Os = 6


class SimulatedRkndio(StateMachineDevice):
    def _initialize_data(self):
        """Initialize all of the device's attributes.
        """
        self._idn = "RIKENFE Prototype v2.0"
        self._connected = True
        self.reset_error()
        self._input_states = ["FALSE"] * NUMBER_OF_D_Is
        self._output_states = ["FALSE"] * NUMBER_OF_D_Os

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])

    @property
    def idn(self):
        """Returns the IDN of the device.

        Returns:
            (string): The IDN of the device.
        """
        return self._idn

    @property
    def connected(self):
        return self._connected

    def get_input_state(self, pin):
        """Gets the state

        Args:
            pin: Pin number of DO

        Returns:
            State pin value - True or False.
            Error: if pin not in range.
        """
        pin = int(pin)
        if pin in range(2, 8):
            return self._input_states[pin - 2]
            self.reset_error()
        else:
            self.error = "The pin is not readable"
            self.status = "The pin is not readable"
            return "ERROR"

    def set_input_state_via_the_backdoor(self, pin, state):
        """Sets the read state of a pin. Called only via the backdoor.

        Args:
            pin: pin number (int 2-7)
            state: True or False

        Returns:
            None
        """
        self._input_states[pin - 2] = state

    def set_output_state(self, pin, state):
        """Gets the state

        Args:
            pin: Pin number of DI
            state (string): TRUE or FALSE

        Returns:
            None
        """
        pin = int(pin)
        if pin not in range(8, 14):
            self._device.error = "The pin is not writeable"
            self._device.status = "The pin is not writeable"
            return "ERROR"
        elif state in ["TRUE", "FALSE"]:
            self._output_states[pin - 8] = state
            self.reset_error()
            return "OK"
        else:
            self._device.error = "Cannot set pin {} to {}".format(pin, state)
            self._device.status = "Cannot set pin {} to {}".format(pin, state)
            return "ERROR"

    def get_output_state_via_the_backdoor(self, pin):
        """Gets the set state of a pin. Called only via the backdoor.

        Args:
            pin: pin number (int 8-13)

        Returns:
            (string): True or False
        """
        return self._output_states[pin - 8]

    def connect(self):
        """Connects the device.

        Returns:
            None
        """
        self._connected = True

    def disconnect(self):
        """Disconnects the device.

        Returns:
            Nome
        """
        self._connected = False

    def reset_error(self):
        self.error = "No error"
        self.status = "No error"
