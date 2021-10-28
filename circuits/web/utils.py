"""
Utilities

This module implements utility functions.
"""

import os
import stat
import struct
import time
import zlib

import httoop

from .exceptions import RangeUnsatisfiable


def is_unix_socket(path):
    if not os.path.exists(path):
        return False

    mode = os.stat(path).st_mode

    return stat.S_ISSOCK(mode)


def compress(body, compress_level):
    """Compress 'body' at the given compress_level."""
    # Header
    yield b'\037\213\010\0' + struct.pack('<L', int(time.time())) + b'\002\377'

    size = 0
    crc = zlib.crc32(b'')

    zobj = zlib.compressobj(
        compress_level,
        zlib.DEFLATED,
        -zlib.MAX_WBITS,
        zlib.DEF_MEM_LEVEL,
        0,
    )

    for chunk in body:
        if not isinstance(chunk, bytes):
            chunk = chunk.encode('utf-8')

        size += len(chunk)
        crc = zlib.crc32(chunk, crc)
        yield zobj.compress(chunk)

    yield zobj.flush() + struct.pack('<l', crc) + struct.pack('<L', size & 0xFFFFFFFF)


def get_ranges(headervalue, content_length):
    """
    Return a list of (start, stop) indices from a Range header, or None.

    Each (start, stop) tuple will be composed of two ints, which are suitable
    for use in a slicing operation. That is, the header "Range: bytes=3-6",
    if applied against a Python string, is requesting resource[3:7]. This
    function will return the list [(3, 7)].

    If this function returns an empty list, you should return HTTP 416.
    """
    if not headervalue:
        return

    headers = httoop.Headers(
        {
            'Range': headervalue,
        }
    )
    try:
        ranges = headers.element('Range')
    except httoop.InvalidHeader as exc:
        raise RangeUnsatisfiable(str(exc))

    return sorted(
        set(
            (start, (stop or content_length - 1) + 1) if start else (content_length - int(stop), content_length)
            for start, stop in ranges.ranges
            if not start or start < content_length
        )
    )
