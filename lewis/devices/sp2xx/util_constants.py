from .util_classes import Direction, ErrorType, Mode

infusion_mode = Mode("i", "I", "Infusion")
withdrawal_mode = Mode("w", "W", "Withdrawal")
infusion_withdrawal_mode = Mode("i/w", "IW", "Infusion/Withdrawal")
withdrawal_infusion_mode = Mode("w/i", "WI", "Withdrawal/Infusion")
continuous = Mode("con", "CON", "Continuous")

MODES = {
    "i": infusion_mode,
    "w": withdrawal_mode,
    "i/w": infusion_withdrawal_mode,
    "w/i": withdrawal_infusion_mode,
    "con": continuous,
}

infusion_direction = Direction("I", "Infusion")
withdrawal_direction = Direction("W", "Withdrawal")

DIRECTIONS = {"I": infusion_direction, "W": withdrawal_direction}

NO_ERROR = ErrorType("No error", 0, "NO_ALARM")
