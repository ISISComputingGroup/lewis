class NeoceraDeviceErrors(object):
    """Class to represent errors."""

    # bad parameter has been encountered
    BAD_PARAMETER = "Bad parameter"

    def __init__(self, *error_list):
        self.errors = error_list
