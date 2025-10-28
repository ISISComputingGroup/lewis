def format_int(i, as_string, length):
    if as_string:
        return str(i) if length is None else str(i)[:length].zfill(length)
    else:
        return i


def format_float(f, as_string):
    return "{0:.2f}".format(f).zfill(5) if as_string else f


def pad_string(s, length, padding_character):
    return s if length is None else s[:length] + (length - len(s)) * padding_character


def convert_raw_to_int(raw):
    if type(raw) == int:
        return raw
    elif type(raw) == str:
        return int(raw.zfill(1))
    else:
        return 0


def convert_raw_to_float(raw):
    try:
        return float(raw)
    except:
        return 0.0


def convert_raw_to_bool(raw):
    return bool(convert_raw_to_int(raw))
