def format_value(f, as_string):
    """Format a floating point value into either a string or return it as is."""
    return "{0:.3f}".format(f) if as_string else f
