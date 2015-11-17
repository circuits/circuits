"""Utilities"""

from circuits.six import iterbytes


def is_ssl_handshake(buf):
    """Detect an SSLv2 or SSLv3 handshake"""

    # SSLv3, TLS 1.1 - 1.3
    v = buf[:3]
    if v in ("\x16\x03\x00", "\x16\x03\x01", "\x16\x03\x02", "\x16\x03\x03", "\x16\x03\x04"):
        return True

    # SSLv2
    v = list(iterbytes(buf[:2])) + [0x00, 0x00]
    if (v[0] & 0x80 == 0x80) and ((v[0] & 0x7f) << 8 | v[1]) > 9:
        return True
