# Module:   utils
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Utilities

This module implements utility functions.
"""

import re
import zlib
import time
import struct
from io import TextIOWrapper
from cgi import FieldStorage
from collections import MutableMapping

try:
    from urllib.parse import urljoin as _urljoin
except ImportError:
    from urlparse import urljoin as _urljoin  # NOQA

try:
    from urllib.parse import parse_qs as _parse_qs
except ImportError:
    from cgi import parse_qs as _parse_qs  # NOQA

from .exceptions import RequestEntityTooLarge

quoted_slash = re.compile("(?i)%2F")
image_map_pattern = re.compile("^[0-9]+,[0-9]+$")


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


def url(request, path="", qs="", script_name=None, base=None, relative=None):
    """Create an absolute URL for the given path.

    If 'path' starts with a slash ('/'), this will return
       - (base + script_name + path + qs).
    If it does not start with a slash, this returns
       - (base + script_name [+ request.path] + path + qs).

    If script_name is None, request will be used
    to find a script_name, if available.

    If base is None, request.base will be used (if available).

    Finally, note that this function can be used to obtain an absolute URL
    for the current request path (minus the querystring) by passing no args.
    If you call url(qs=request.qs), you should get the
    original browser URL (assuming no internal redirections).

    If relative is False the output will be an absolute URL
    (including the scheme, host, vhost, and script_name).
    If True, the output will instead be a URL that is relative to the
    current request path, perhaps including '..' atoms. If relative is
    the string 'server', the output will instead be a URL that is
    relative to the server root; i.e., it will start with a slash.
    """
    if qs:
        qs = '?' + qs

    if not path.startswith("/"):
        # Append/remove trailing slash from request.path as needed
        # (this is to support mistyped URL's without redirecting;
        # if you want to redirect, use tools.trailing_slash).
        pi = request.path
        if request.index is True:
            if not pi.endswith('/'):
                pi = pi + '/'
        elif request.index is False:
            if pi.endswith('/') and pi != '/':
                pi = pi[:-1]

        if path == "":
            path = pi
        else:
            path = _urljoin(pi, path)

    if script_name is None:
        script_name = request.script_name
    if base is None:
        base = request.base

    newurl = base + script_name + path + qs

    if './' in newurl:
        # Normalize the URL by removing ./ and ../
        atoms = []
        for atom in newurl.split('/'):
            if atom == '.':
                pass
            elif atom == '..':
                try:
                    atoms.pop()
                except IndexError:
                    pass
            else:
                atoms.append(atom)
        newurl = '/'.join(atoms)

    # At this point, we should have a fully-qualified absolute URL.

    # See http://www.ietf.org/rfc/rfc2396.txt
    if relative == 'server':
        # "A relative reference beginning with a single slash character is
        # termed an absolute-path reference, as defined by <abs_path>..."
        # This is also sometimes called "server-relative".
        newurl = '/' + '/'.join(newurl.split('/', 3)[3:])
    elif relative:
        # "A relative reference that does not begin with a scheme name
        # or a slash character is termed a relative-path reference."
        old = url().split('/')[:-1]
        new = newurl.split('/')
        while old and new:
            a, b = old[0], new[0]
            if a != b:
                break
            old.pop(0)
            new.pop(0)
        new = (['..'] * len(old)) + new
        newurl = '/'.join(new)

    return newurl


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
            result.append((start, stop + 1))
        else:
            if not stop:
                # See rfc quote above.
                return None
            # Negative subscript (last N bytes)
            result.append((content_length - int(stop), content_length))

    return result


class IOrderedDict(dict, MutableMapping):
    'Dictionary that remembers insertion order with insensitive key'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as for regular dictionaries.

    # The internal self.__map dictionary maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # Each link is stored as a list of length three:  [PREV, NEXT, KEY].

    def __init__(self, *args, **kwds):
        '''Initialize an ordered dictionary.  Signature is the same as for
        regular dictionaries, but keyword arguments are not recommended
        because their insertion order is arbitrary.

        '''
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__root
        except AttributeError:
            self.__root = root = [None, None, None]     # sentinel node
            PREV = 0
            NEXT = 1
            root[PREV] = root[NEXT] = root
            self.__map = {}
        self.__lower = {}
        self.update(*args, **kwds)

    def __setitem__(self, key, value, PREV=0, NEXT=1, dict_setitem=dict.__setitem__):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link which goes at the end of the linked
        # list, and the inherited dictionary is updated with the new key/value pair.
        if key not in self:
            root = self.__root
            last = root[PREV]
            last[NEXT] = root[PREV] = self.__map[key] = [last, root, key]
            self.__lower[key.lower()] = key
        key = self.__lower[key.lower()]
        dict_setitem(self, key, value)

    def __delitem__(self, key, PREV=0, NEXT=1, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> del od[y]'
        # Deleting an existing item uses self.__map to find the link which is
        # then removed by updating the links in the predecessor and successor nodes.
        if key in self:
            key = self.__lower.pop(key.lower())

        dict_delitem(self, key)
        link = self.__map.pop(key)
        link_prev = link[PREV]
        link_next = link[NEXT]
        link_prev[NEXT] = link_next
        link_next[PREV] = link_prev

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        if key in self:
            key = self.__lower.get(key.lower())
        return dict_getitem(self, key)

    def __contains__(self, key):
        return key.lower() in self.__lower

    def __iter__(self, NEXT=1, KEY=2):
        'od.__iter__() <==> iter(od)'
        # Traverse the linked list in order.
        root = self.__root
        curr = root[NEXT]
        while curr is not root:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self, PREV=0, KEY=2):
        'od.__reversed__() <==> reversed(od)'
        # Traverse the linked list in reverse order.
        root = self.__root
        curr = root[PREV]
        while curr is not root:
            yield curr[KEY]
            curr = curr[PREV]

    def __reduce__(self):
        'Return state information for pickling'
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__root
        del self.__map, self.__root
        inst_dict = vars(self).copy()
        self.__map, self.__root = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def clear(self):
        'od.clear() -> None.  Remove all items from od.'
        try:
            for node in self.__map.values():
                del node[:]
            self.__root[:] = [self.__root, self.__root, None]
            self.__map.clear()
        except AttributeError:
            pass
        dict.clear(self)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items
    __ne__ = MutableMapping.__ne__

    def popitem(self, last=True):
        '''od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order if false.

        '''
        if not self:
            raise KeyError('dictionary is empty')
        key = next(reversed(self) if last else iter(self))
        value = self.pop(key)
        return key, value

    def __repr__(self):
        'od.__repr__() <==> repr(od)'
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))

    def copy(self):
        'od.copy() -> a shallow copy of od'
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S
        and values equal to v (which defaults to None).

        '''
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
        while comparison to a regular mapping is order-insensitive.

        '''
        if isinstance(other, IOrderedDict):
            return len(self)==len(other) and \
                    set(self.items()) == set(other.items())
        return dict.__eq__(self, other)

    def __del__(self):
        self.clear()                # eliminate cyclical references


def is_ssl_handshake(buf):
    """Detect an SSLv2 or SSLv3 handshake"""

    v = buf[0:3]
    if v in ["\x16\x03\x00", "\x16\x03\x01", "\x16\x03\x02"]:
        return True

    # XXX: Add SSLv2 detection ...
