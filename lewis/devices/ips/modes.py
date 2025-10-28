from enum import Enum


class Activity(Enum):
    HOLD = "Hold"
    TO_SETPOINT = "To Setpoint"
    TO_ZERO = "To Zero"
    CLAMP = "Clamped"


class Control(Enum):
    LOCAL_LOCKED = "Local & Locked"
    REMOTE_LOCKED = "Remote & Unlocked"
    LOCAL_UNLOCKED = "Local & Unlocked"
    REMOTE_UNLOCKED = "Remote & Unlocked"
    AUTO_RUNDOWN = "Auto-Run-Down"


class SweepMode(Enum):
    TESLA_FAST = "Tesla Fast"


class Mode(Enum):
    FAST = "Fast"
    SLOW = "Slow"
