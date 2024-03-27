#!/usr/bin/env python
from io import BytesIO

from circuits.web.utils import compress, get_ranges


try:
    from gzip import decompress
except ImportError:
    import zlib

    decompress = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress


def test_ranges() -> None:
    assert get_ranges('bytes=3-6', 8) == [(3, 7)]
    assert get_ranges('bytes=2-4,-1', 8) == [(2, 5), (7, 8)]


def test_gzip() -> None:
    s = b'Hello World!'
    contents = BytesIO(s)
    compressed = b''.join(compress(contents, 1))
    uncompressed = decompress(compressed)
    assert uncompressed == s
    contents.close()
