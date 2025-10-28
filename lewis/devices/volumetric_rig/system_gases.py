from .gas import Gas


class SystemGases(object):
    """The collection of gases that are available within the system."""

    def __init__(self, gases=list()):
        self._gases = set()
        self._add_gases(gases)

    def gas_by_index(self, index):
        return self._get_by_method(index, "index")

    def gas_by_name(self, name):
        return self._get_by_method(name, "name")

    def _get_by_method(self, value, method):
        try:
            return next(g for g in self._gases if getattr(g, method)() == value)
        except StopIteration:
            return None

    def _add_gases(self, iterable):
        self._gases = set.union(
            self._gases, {g for g in iterable if isinstance(g, Gas)}
        )

    def gases(self):
        return sorted(list(self._gases), key=lambda g: g.index())

    def gas_count(self):
        return len(self._gases)
