from .utilities import format_int, pad_string


class Gas(object):
    """A gas within the system, identified by either its name or an integer index.
    """

    def __init__(self, index, name):
        assert type(index) is int and type(name) is str
        self._index = index
        self._name = name

    def name(self, length=None, padding_character=" "):
        return pad_string(self._name, length, padding_character)

    def index(self, as_string=False, length=2):
        return format_int(self._index, as_string, length)
