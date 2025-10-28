from enum import Enum


class RampTarget(Enum):
    ZERO = 0
    MID = 1
    MAX = 2


class RampDirection(Enum):
    NEGATIVE = 0
    ZERO = 1
    POSITIVE = 2
