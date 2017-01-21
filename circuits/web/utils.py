"""Utilities

This module implements utility functions.
"""
import os
import re
import stat
import struct
import time
import zlib
from cgi import FieldStorage
from io import TextIOWrapper
from math import sqrt

from circuits.net.utils import is_ssl_handshake  # noqa
from circuits.six.moves.urllib_parse import parse_qs as _parse_qs

from .exceptions import RangeUnsatisfiable, RequestEntityTooLarge

quoted_slash = re.compile("(?i)%2F")
image_map_pattern = re.compile("^[0-9]+,[0-9]+$")


def is_unix_socket(path):
    if not os.path.exists(path):
        return False

    mode = os.stat(path).st_mode

    return stat.S_ISSOCK(mode)


def average(xs):
    return sum(xs) * 1.0 / len(xs)


def variance(xs):
    avg = average(xs)
    return list(map(lambda x: (x - avg) ** 2, xs))


def stddev(xs):
    return sqrt(average(variance(xs)))


def parse_body(request, response, params):
    if "Content-Type" not in request.headers:
        request.headers["Content-Type"] = ""

    try:
        form = FieldStorage(
            environ={"REQUEST_METHOD": "POST"},
            fp=TextIOWrapper(request.body),
            headers=request.headers,
            keep_blank_values=True
        )
    except Exception as e:
        if e.__class__.__name__ == 'MaxSizeExceeded':
            # Post data is too big
            raise RequestEntityTooLarge()
        raise

    if form.file:
        request.body = form.file
    else:
        params.update(dictform(form))


def parse_qs(query_string, keep_blank_values=True):
    """parse_qs(query_string) -> dict

    Build a params dictionary from a query_string.
    If keep_blank_values is True (the default), keep
    values that are blank.
    """

    if image_map_pattern.match(query_string):
        # Server-side image map. Map the coords to "x" and "y"
        # (like CGI::Request does).
        pm = query_string.split(",")
        return {"x": int(pm[0]), "y": int(pm[1])}
    else:
        pm = _parse_qs(query_string, keep_blank_values)
        return dict((k, v[0]) for k, v in pm.items() if v)


def dictform(form):
    d = {}
    for key in list(form.keys()):
        values = form[key]
        if isinstance(values, list):
            d[key] = []
            for item in values:
                if item.filename is not None:
                    value = item  # It's a file upload
                else:
                    value = item.value  # It's a regular field
                d[key].append(value)
        else:
            if values.filename is not None:
                value = values  # It's a file upload
            else:
                value = values.value  # It's a regular field
            d[key] = value
    return d


def compress(body, compress_level):
    """Compress 'body' at the given compress_level."""

    # Header
    yield b"\037\213\010\0" \
        + struct.pack("<L", int(time.time())) \
        + b"\002\377"

    size = 0
    crc = zlib.crc32(b"")

    zobj = zlib.compressobj(
        compress_level,
        zlib.DEFLATED,
        -zlib.MAX_WBITS,
        zlib.DEF_MEM_LEVEL,
        0,
    )

    for chunk in body:
        if not isinstance(chunk, bytes):
            chunk = chunk.encode("utf-8")

        size += len(chunk)
        crc = zlib.crc32(chunk, crc)
        yield zobj.compress(chunk)

    yield zobj.flush() \
        + struct.pack("<l", crc) \
        + struct.pack("<L", size & 0xFFFFFFFF)


def get_ranges(headervalue, content_length):
    """Return a list of (start, stop) indices from a Range header, or None.

    Each (start, stop) tuple will be composed of two ints, which are suitable
    for use in a slicing operation. That is, the header "Range: bytes=3-6",
    if applied against a Python string, is requesting resource[3:7]. This
    function will return the list [(3, 7)].

    If this function returns an empty list, you should return HTTP 416.
    """

    if not headervalue:
        return None

    result = []
    bytesunit, byteranges = headervalue.split("=", 1)
    for brange in byteranges.split(","):
        start, stop = [x.strip() for x in brange.split("-", 1)]
        if start:
            if not stop:
                stop = content_length - 1
            start, stop = list(map(int, (start, stop)))
            if start >= content_length:
                # From rfc 2616 sec 14.16:
                # "If the server receives a request (other than one
                # including an If-Range request-header field) with an
                # unsatisfiable Range request-header field (that is,
                # all of whose byte-range-spec values have a first-byte-pos
                # value greater than the current length of the selected
                # resource), it SHOULD return a response code of 416
                # (Requested range not satisfiable)."
                continue
            if stop < start:
                # From rfc 2616 sec 14.16:
                # "If the server ignores a byte-range-spec because it
                # is syntactically invalid, the server SHOULD treat
                # the request as if the invalid Range header field
                # did not exist. (Normally, this means return a 200
                # response containing the full entity)."
                return None
            # Prevent duplicate ranges. See Issue #59
            if (start, stop + 1) not in result:
                result.append((start, stop + 1))
        else:
            if not stop:
                # See rfc quote above.
                return None
            # Negative subscript (last N bytes)
            # Prevent duplicate ranges. See Issue #59
            if (content_length - int(stop), content_length) not in result:
                result.append((content_length - int(stop), content_length))

    # Can we satisfy the requested Range?
    # If we have an exceedingly high standard deviation
    # of Range(s) we reject the request.
    # See Issue #59

    if len(result) > 1 and stddev([x[1] - x[0] for x in result]) > 2.0:
        raise RangeUnsatisfiable()

    return result
