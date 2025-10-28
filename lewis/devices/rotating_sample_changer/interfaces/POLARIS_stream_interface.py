from lewis.adapters.stream import Cmd, StreamInterface

from ..states import Errors


class POLARISSampleChangerStreamInterface(StreamInterface):
    protocol = "POLARIS"

    commands = {
        Cmd("get_id", "^id$"),
        Cmd("get_position", "^po$"),
        Cmd("get_status", "^st$"),
        Cmd("go_back", "^bk$"),
        Cmd("go_fwd", "^fw$"),
        Cmd("halt", "^ht$"),
        Cmd("initialise", "^in$"),
        Cmd("lower_arm", "^lo$"),
        Cmd("move_to", "^ma(0[1-9]|[1][0-9]|20)$", argument_mappings=[int]),
        Cmd("move_to_without_lowering", "^mn(0[1-9]|[1][0-9]|20)$", argument_mappings=[int]),
        Cmd("raise_arm", "^ra$"),
        Cmd("retrieve_sample", "^rt$"),
    }

    error_codes = {
        Errors.NO_ERR: 0,
        Errors.ERR_INV_DEST: 5,
        Errors.ERR_NOT_INITIALISED: 6,
        Errors.ERR_ARM_DROPPED: 7,
        Errors.ERR_ARM_UP: 8,
        Errors.ERR_CANT_ROT_IF_NOT_UP: 10,
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def get_id(self):
        return "0001 0001 ISIS Polaris Sample Changer V"

    def get_position(self):
        return "Position = {:2d}".format(int(self._device.car_pos))

    def get_status(self):
        lowered = self._device.get_arm_lowered()

        # Based on testing with actual device, appears to be different than doc
        return_string = "{0:b}01{1:b}{2:b}{3:b}0{4:b}"
        return_string = return_string.format(
            not lowered,
            self._device.is_car_at_one(),
            not lowered,
            lowered,
            self._device.is_moving(),
        )

        return_string += "{:1d}".format(int(self._device.current_err))
        return_string += " {:2d}".format(int(self._device.car_pos))

        return return_string

    def go_back(self):
        self._device.go_backward()

    def go_fwd(self):
        self._device.go_forward()

    def halt(self):
        return ""

    def initialise(self):
        self._device.init()

    def move_to(self, position):
        self._device.move_to(position, True)

    def move_to_without_lowering(self, position):
        self._device.move_to(position, False)

    def lower_arm(self):
        self._device.set_arm(True)

    def raise_arm(self):
        self._device.set_arm(False)

    def retrieve_sample(self):
        self._device.sample_retrieved = True

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
        return "??"
