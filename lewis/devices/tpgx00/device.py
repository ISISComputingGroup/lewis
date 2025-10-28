from collections import OrderedDict
from enum import Enum, unique

from lewis.devices import StateMachineDevice

from .states import DefaultState


@unique
class Units(Enum):
    hPascal = object()
    mbar = object()
    Torr = object()
    Pa = object()
    Micron = object()
    Volt = object()
    Ampere = object()


@unique
class ChannelStatus(Enum):
    DATA_OK = object()
    UNDERRANGE = object()
    OVERRANGE = object()
    POINT_ERROR = object()
    POINT_OFF = object()
    NO_HARDWARE = object()


@unique
class SFAssignment(Enum):
    OFF = object()
    A1 = object()
    A2 = object()
    B1 = object()
    B2 = object()
    A1_SELF_MON = object()
    A2_SELF_MON = object()
    B1_SELF_MON = object()
    B2_SELF_MON = object()
    ON = object()


@unique
class SFStatus(Enum):
    OFF = object()
    ON = object()


@unique
class ErrorStatus(Enum):
    NO_ERROR = object()
    DEVICE_ERROR = object()
    NO_HARDWARE = object()
    INVALID_PARAM = object()
    SYNTAX_ERROR = object()


@unique
class ReadState(Enum):
    A1 = object()
    A2 = object()
    B1 = object()
    B2 = object()
    UNI = object()
    UNI0 = object()
    UNI1 = object()
    UNI2 = object()
    UNI3 = object()
    UNI4 = object()
    UNI5 = object()
    UNI6 = object()
    F1 = object()
    F2 = object()
    F3 = object()
    F4 = object()
    FA = object()
    FB = object()
    FS1 = object()
    FS2 = object()
    FS3 = object()
    FS4 = object()
    FSA = object()
    FSB = object()
    SPS = object()
    ERR = object()


class CircuitAssignment:
    """This object represents settings for a circuit in the device.
    these settings are: high_threshold(float), high_exponent(int),
    low_threshold(float), low_exponent(int), circuit_assignment(SFAssignment enum member)
    """

    def __init__(
        self,
        high_threshold=0.0,
        high_exponent=0,
        low_threshold=0.0,
        low_exponent=0,
        circuit_assignment="A1",
    ):
        """Default constructor.
        """
        self.high_threshold = high_threshold
        self.high_exponent = high_exponent
        self.low_threshold = low_threshold
        self.low_exponent = low_exponent
        self.circuit_assignment = SFAssignment[circuit_assignment]


class SimulatedTpgx00(StateMachineDevice):
    """Simulated device for both the TPG300 and TPG500.
    """

    def _initialize_data(self):
        """Sets the initial state of the device.
        """
        self.__pressure_a1 = 0.0
        self.__pressure_a2 = 0.0
        self.__pressure_b1 = 0.0
        self.__pressure_b2 = 0.0
        self.__pressure_status_a1 = ChannelStatus["DATA_OK"]
        self.__pressure_status_a2 = ChannelStatus["DATA_OK"]
        self.__pressure_status_b1 = ChannelStatus["DATA_OK"]
        self.__pressure_status_b2 = ChannelStatus["DATA_OK"]
        self.__units = Units["mbar"]
        self.__connected = None
        self.__readstate = None
        self.__switching_functions = {
            "1": CircuitAssignment(),
            "2": CircuitAssignment(),
            "3": CircuitAssignment(),
            "4": CircuitAssignment(),
            "A": CircuitAssignment(),
            "B": CircuitAssignment(),
        }
        self.__switching_function_to_set = CircuitAssignment()
        self.__switching_functions_status = {
            "1": SFStatus["OFF"],
            "2": SFStatus["OFF"],
            "3": SFStatus["OFF"],
            "4": SFStatus["OFF"],
            "A": SFStatus["OFF"],
            "B": SFStatus["OFF"],
        }
        self.__switching_function_assignment = {
            "1": SFAssignment["OFF"],
            "2": SFAssignment["OFF"],
            "3": SFAssignment["OFF"],
            "4": SFAssignment["OFF"],
            "A": SFAssignment["OFF"],
            "B": SFAssignment["OFF"],
        }
        self.__on_timer = 0
        self.__error_status = ErrorStatus["NO_ERROR"]
        self.connect()

    @staticmethod
    def _get_state_handlers():
        """Returns: states and their names
        """
        return {DefaultState.NAME: DefaultState()}

    @staticmethod
    def _get_initial_state():
        """Returns: the name of the initial state
        """
        return DefaultState.NAME

    @staticmethod
    def _get_transition_handlers():
        """Returns: the state transitions
        """
        return OrderedDict()

    @property
    def pressure_a1(self):
        """Returns the value of the A1 pressure sensor.

        Returns:
            float: Pressure A1 value.
        """
        return self.__pressure_a1

    @pressure_a1.setter
    def pressure_a1(self, value):
        """Sets the A1 pressure sensor.

        Args:
            value: Value to set A1 pressure sensor to.

        Returns:
            None
        """
        self.__pressure_a1 = value

    @property
    def pressure_a2(self):
        """Returns the value of the A2 pressure sensor.

        Returns:
            float: Pressure A1 value.
        """
        return self.__pressure_a2

    @pressure_a2.setter
    def pressure_a2(self, value):
        """Sets the B1 pressure sensor.

        Args:
            value: Value to set B1 pressure sensor to.

        Returns:
            None
        """
        self.__pressure_a2 = value

    @property
    def pressure_b1(self):
        """Returns the value of the A2 pressure sensor.

        Returns:
            float: Pressure A1 value.
        """
        return self.__pressure_b1

    @pressure_b1.setter
    def pressure_b1(self, value):
        """Sets the B1 pressure sensor.

        Args:
            value: Value to set B1 pressure sensor to.

        Returns:
            None
        """
        self.__pressure_b1 = value

    @property
    def pressure_b2(self):
        """Returns the value of the B2 pressure sensor.

        Returns:
            float: Pressure B2 value.
        """
        return self.__pressure_b2

    @pressure_b2.setter
    def pressure_b2(self, value):
        """Sets the B2 pressure sensor.

        Args:
            value: Value to set B2 pressure sensor to.

        Returns:
            None
        """
        self.__pressure_b2 = value

    @property
    def pressure_status_a1(self):
        """Returns the status of the A1 pressure sensor

        Returns:
            Enum memeber: A1 pressure sensor status
        """
        return self.__pressure_status_a1

    @pressure_status_a1.setter
    def pressure_status_a1(self, value):
        """Sets the status of the A1 pressure sensor
        (Only used via backdoor)

        Args:
            value: Enum member to be set as the status
        Returns:
            None
        """
        self.__pressure_status_a1 = value

    @property
    def pressure_status_a2(self):
        """Returns the status of the A2 pressure sensor

        Returns:
            Enum memeber: A2 pressure sensor status
        """
        return self.__pressure_status_a2

    @pressure_status_a2.setter
    def pressure_status_a2(self, value):
        """Sets the status of the A2 pressure sensor
        (Only used via backdoor)

        Args:
            value: Enum member to be set as the status
        Returns:
            None
        """
        self.__pressure_status_a2 = value

    @property
    def pressure_status_b1(self):
        """Returns the status of the B1 pressure sensor

        Returns:
            Enum memeber: B1 pressure sensor status
        """
        return self.__pressure_status_b1

    @pressure_status_b1.setter
    def pressure_status_b1(self, value):
        """Sets the status of the B1 pressure sensor
        (Only used via backdoor)

        Args:
            value: Enum member to be set as the status
        Returns:
            None
        """
        self.__pressure_status_b1 = value

    @property
    def pressure_status_b2(self):
        """Returns the status of the B2 pressure sensor

        Returns:
            Enum memeber: B2 pressure sensor status
        """
        return self.__pressure_status_b2

    @pressure_status_b2.setter
    def pressure_status_b2(self, value):
        """Sets the status of the B2 pressure sensor
        (Only used via backdoor)

        Args:
            value: Enum member to be set as the status
        Returns:
            None
        """
        self.__pressure_status_b2 = value

    @property
    def units(self):
        """Returns units currently set of the device.

        Returns:
            unit (Enum member): Enum member of Units Enum.
        """
        return self.__units

    @units.setter
    def units(self, units):
        """Sets the devices units.

        Args:
            units: Enum member of Units.

        Returns:
            None
        """
        self.__units = units

    @property
    def switching_functions_status(self):
        """Returns status of the switching functions.

        Returns:
            a dictionary of 6 Enum members which can be SFStatus.OFF (off) or SFStatus.ON (on)
        """
        return self.__switching_functions_status

    @switching_functions_status.setter
    def switching_functions_status(self, statuses):
        """Sets the status of the switching functions.

        Args:
            status: list of 6 values which can be 'OFF' or 'ON'
        Returns:
            None
        """
        for key, status in zip(self.__switching_functions_status.keys(), statuses):
            self.__switching_functions_status[key] = SFStatus[status]

    @property
    def switching_functions(self):
        """Returns the settings of a switching function

        Returns:
            list of 6 CircuitAssignment instances
        """
        return self.__switching_functions

    @switching_functions.setter
    def switching_functions(self, function_list):
        """Sets the status of the switching functions.

        Args:
            function_list: list of 6 CircuitAssignment instances
        Returns:
            None
        """
        self.__switching_functions = function_list

    @property
    def switching_function_to_set(self):
        """Returns the thresholds of the switching function that will be saved upon receiving ENQ signal.

        Returns:
            CircuitAssignment instance
        """
        return self.__switching_function_to_set

    @switching_function_to_set.setter
    def switching_function_to_set(self, function):
        """Sets the thresholds of the switching function that will be saved upon receiving ENQ signal.

        Args:
            function: CircuitAssignment instance
        Returns:
            None
        """
        self.__switching_function_to_set = function

    @property
    def switching_function_assignment(self, function):
        """Returns the assignment of the current switching function

        Args:
            function: (string) the switching function to retrieve the switching function assignment for.
        """
        return self.__switching_function_assignment[function]

    @property
    def on_timer(self):
        """Returns the ON-Timer property

        Returns:
            int: (0-100) ON-Timer value
        """
        return self.__on_timer

    @property
    def error_status(self):
        """Returns the error status of the device

        Returns:
            Enum: ErrorStatus code of the device
        """
        return self.__error_status

    @error_status.setter
    def error_status(self, error):
        """Sets the error status of the device. Called only via the backdoor using lewis.

        Args:
            string: the enum name of the error status to be set

        Returns:
            None
        """
        self.__error_status = ErrorStatus[error]

    @property
    def connected(self):
        """Returns the current connected state.

        Returns:
            bool: Current connected state.
        """
        return self.__connected

    def connect(self):
        """Connects the device.

        Returns:
            None
        """
        self.__connected = True

    def disconnect(self):
        """Disconnects the device.

        Returns:
            None
        """
        self.__connected = False

    @property
    def readstate(self):
        """Returns the readstate for the device

        Returns:
            Enum: Readstate of the device.
        """
        return self.__readstate

    @readstate.setter
    def readstate(self, state):
        """Sets the readstate of the device

        Args:
            state: (string) readstate name of the device to be set

        Returns:
            None
        """
        self.__readstate = ReadState[state]

    def backdoor_get_unit(self):
        """Gets unit on device. Called only via the backdoor using lewis.

        Returns:
            unit (string): Unit enum name
        """
        return self.units.name

    def backdoor_get_switching_fn(self):
        """Gets the current switching function in use on the device.
        Called only via the backdoor using lewis.

        Returns:
            string: SFAssignment member name
        """
        return self.switching_function_to_set.circuit_assignment.name

    def backdoor_set_switching_function_status(self, statuses):
        """Sets status of switching functions. Called only via the backdoor using lewis.

        Args:
            status: list of 6 values (strings) which can be 'OFF' or 'ON'

        Returns:
            None
        """
        self.switching_functions_status = statuses

    def backdoor_set_pressure_status(self, channel, status):
        """Sets the pressure status of the specified channel. Called only via the backdoor using lewis.

        Args:
            channel (string): the pressure channel to set to
            status (string): the name of the pressure status Enum to be set

        Returns:
            None
        """
        status_suffix = "pressure_status_{}".format(channel.lower())
        setattr(self, status_suffix, ChannelStatus[status])

    def backdoor_set_error_status(self, error):
        """Sets the current error status on the device. Called only via the backdoor using lewis.

        Args:
            status (string): the enum name of the error status to be set.

        Returns:
            None
        """
        self.error_status = error
