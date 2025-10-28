from lewis.adapters.stream import Cmd, StreamInterface

from ..states import Errors


class HRPDSampleChangerStreamInterface(StreamInterface):
    protocol = "HRPD"

    commands = {
        Cmd("get_id", "^id$"),
        Cmd("get_position", "^po$"),
        Cmd("get_status", "^st$"),
        Cmd("go_back", "^bk$"),
        Cmd("go_fwd", "^fw$"),
        Cmd("halt", "^ht$"),
        Cmd("initialise", "^in$"),
        Cmd("lower_arm", "^lo$"),
        Cmd("move_to", "^ma([0-9]{2})$", argument_mappings=[int]),
        Cmd("move_to_without_lowering", "^mn([0-9]{2})$", argument_mappings=[int]),
        Cmd("raise_arm", "^ra$"),
        Cmd("read_variable", "^vr([0-9]{4})$", argument_mappings=[int]),
        Cmd("retrieve_sample", "^rt$"),
    }

    error_codes = {
        Errors.NO_ERR: 0,
        Errors.ERR_INV_DEST: 5,
        Errors.ERR_NOT_INITIALISED: 6,
        Errors.ERR_ARM_DROPPED: 7,
        Errors.ERR_ARM_UP: 8,
        Errors.ERR_CANT_ROT_IF_NOT_UP: 7,
    }

    in_terminator = "\r"
    out_terminator = "\r\n"

    def _check_error_code(self, code):
        if code == Errors.NO_ERR:
            return "ok"
        else:
            self._device.current_err = code
            return "rf-%02d" % code

    def get_id(self):
        return "0001 0001 ISIS HRPD Sample Changer V1.00"

    def get_position(self):
        return "Position = {:2d}".format(int(self._device.car_pos))

    def get_status(self):
        lowered = self._device.get_arm_lowered()

        # Based on testing with actual device, appears to be different than doc
        return_string = "01000{0:b}01{1:b}{2:b}{3:b}00000"
        return_string = return_string.format(
            not lowered, self._device.is_car_at_one(), not lowered, lowered
        )

        return_string += " 0 {:b}".format(self._device.is_moving())

        return_error = int(self.error_codes[self._device.current_err])

        return_string += " {:2d}".format(return_error)
        return_string += " {:2d}".format(int(self._device.car_pos))

        return return_string

    def go_back(self):
        return self._check_error_code(self._device.go_backward())

    def go_fwd(self):
        return self._check_error_code(self._device.go_forward())

    def read_variable(self, variable):
        return "- VR " + str(variable) + " = 17 hx 11"

    def halt(self):
        return "ok"

    def initialise(self):
        return self._check_error_code(self._device.init())

    def move_to(self, position):
        return self._check_error_code(self._device.move_to(position, True))

    def move_to_without_lowering(self, position):
        return self._check_error_code(self._device.move_to(position, False))

    def lower_arm(self):
        return self._check_error_code(self._device.set_arm(True))

    def raise_arm(self):
        return self._check_error_code(self._device.set_arm(False))

    def retrieve_sample(self):
        self._device.sample_retrieved = True
        return "ok"

    def handle_error(self, request, error):
        print("An error occurred at request " + repr(request) + ": " + repr(error))
