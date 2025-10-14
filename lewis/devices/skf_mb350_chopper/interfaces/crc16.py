from lewis.utils.byte_conversions import BYTE, int_to_raw_bytes


def crc16_matches(data, expected):
    """:param data: The input, an iterable of characters
    :param expected: The expected checksum, an iterable of two characters
    :return: true if the checksum of 'input' is equal to 'expected', false otherwise.
    """
    return crc16(data) == expected


def crc16(data):
    """CRC algorithm, translated to python from the C code in appendix A of the manual.
    :param data: the data to checksum
    :return: the checksum
    """
    crc = 0xFFFF

    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1

            crc %= BYTE**2

    return int_to_raw_bytes(crc, 2, low_byte_first=True)
