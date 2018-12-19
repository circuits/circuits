"""Headers Support

This module implements support for parsing and handling headers.
"""
import re

from circuits.six import b, iteritems, u

# Regular expression that matches `special' characters in parameters, the
# existance of which force quoting of the parameter value.

tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')
q_separator = re.compile(r'; *q *=')


def _formatparam(param, value=None, quote=1):
    """Convenience function to format and return a key=value pair.

    This will quote the value if needed or if quote is true.
    """
    if value is not None and len(value) > 0:
        if quote or tspecials.search(value):
            value = value.replace('\\', '\\\\').replace('"', r'\"')
            return '%s="%s"' % (param, value)
        else:
            return '%s=%s' % (param, value)
    else:
        return param


def header_elements(fieldname, fieldvalue):
    """Return a sorted HeaderElement list.

    Returns a sorted HeaderElement list
    from a comma-separated header string.
    """

    if not fieldvalue:
        return []

    result = []
    for element in fieldvalue.split(","):
        if fieldname.startswith("Accept") or fieldname == 'TE':
            hv = AcceptElement.from_str(element)
        else:
            hv = HeaderElement.from_str(element)
        result.append(hv)

    return list(reversed(sorted(result)))


class HeaderElement(object):

    """An element (with parameters) from an HTTP header's element list."""

    def __init__(self, value, params=None):
        self.value = value
        if params is None:
            params = {}
        self.params = params

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        p = [";%s=%s" % (k, v) for k, v in iteritems(self.params)]
        return "%s%s" % (self.value, "".join(p))

    def __bytes__(self):
        return b(self.__str__())

    def __unicode__(self):
        return u(self.__str__())

    def parse(elementstr):
        """Transform 'token;key=val' to ('token', {'key': 'val'})."""
        # Split the element into a value and parameters. The 'value' may
        # be of the form, "token=token", but we don't split that here.
        atoms = [x.strip() for x in elementstr.split(";") if x.strip()]
        if not atoms:
            initial_value = ''
        else:
            initial_value = atoms.pop(0).strip()
        params = {}
        for atom in atoms:
            atom = [x.strip() for x in atom.split("=", 1) if x.strip()]
            key = atom.pop(0)
            if atom:
                val = atom[0]
            else:
                val = ""
            params[key] = val
        return initial_value, params
    parse = staticmethod(parse)

    @classmethod
    def from_str(cls, elementstr):
        """Construct an instance from a string of the form 'token;key=val'."""
        ival, params = cls.parse(elementstr)
        return cls(ival, params)


class AcceptElement(HeaderElement):

    """An element (with parameters) from an Accept* header's element list.

    AcceptElement objects are comparable; the more-preferred object will be
    "less than" the less-preferred object. They are also therefore sortable;
    if you sort a list of AcceptElement objects, they will be listed in
    priority order; the most preferred value will be first. Yes, it should
    have been the other way around, but it's too late to fix now.
    """

    @classmethod
    def from_str(cls, elementstr):
        qvalue = None
        # The first "q" parameter (if any) separates the initial
        # media-range parameter(s) (if any) from the accept-params.
        atoms = q_separator.split(elementstr, 1)
        media_range = atoms.pop(0).strip()
        if atoms:
            # The qvalue for an Accept header can have extensions. The other
            # headers cannot, but it's easier to parse them as if they did.
            qvalue = HeaderElement.from_str(atoms[0].strip())

        media_type, params = cls.parse(media_range)
        if qvalue is not None:
            params["q"] = qvalue
        return cls(media_type, params)

    def qvalue(self):
        val = self.params.get("q", "1")
        if isinstance(val, HeaderElement):
            val = val.value
        return float(val)
    qvalue = property(qvalue, doc="The qvalue, or priority, of this value.")

    def __eq__(self, other):
        return self.qvalue == other.qvalue

    def __lt__(self, other):
        if self.qvalue == other.qvalue:
            return str(self) < str(other)
        else:
            return self.qvalue < other.qvalue


class CaseInsensitiveDict(dict):

    """A case-insensitive dict subclass.

    Each key is changed on entry to str(key).title().
    """

    def __init__(self, *args, **kwargs):
        d = dict(*args, **kwargs)
        for key, value in iteritems(d):
            dict.__setitem__(self, str(key).title(), value)
        dict.__init__(self)

    def __getitem__(self, key):
        return dict.__getitem__(self, str(key).title())

    def __setitem__(self, key, value):
        dict.__setitem__(self, str(key).title(), value)

    def __delitem__(self, key):
        dict.__delitem__(self, str(key).title())

    def __contains__(self, key):
        return dict.__contains__(self, str(key).title())

    def get(self, key, default=None):
        return dict.get(self, str(key).title(), default)

    def update(self, E):
        for k in E.keys():
            self[str(k).title()] = E[k]

    @classmethod
    def fromkeys(cls, seq, value=None):
        newdict = cls()
        for k in seq:
            newdict[k] = value
        return newdict

    def setdefault(self, key, x=None):
        key = str(key).title()
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            self[key] = x
            return x

    def pop(self, key, default=None):
        return dict.pop(self, str(key).title(), default)


class Headers(CaseInsensitiveDict):
    """
    This class implements a storage for headers as key value pairs.
    The underlying model of a case insensitive dict matches the requirements
    for headers quite well, because usually header keys are unique. If
    several values may be associated with a header key, most HTTP headers
    represent the values as an enumeration using a comma as item separator.

    There is, however one exception (currently) to this rule. In order to
    set several cookies, there should be multiple headers with the same
    key, each setting one cookie ("Set-Cookie: some_cookie").

    This is modeled by having either a string (common case) or a list
    (cookie case) as value in the underlying dict. In order to allow
    easy iteration over all headers as they appear in the HTTP request,
    the items() method expands associated lists of values. So if you have
    { "Set-Cookie": [ "cookie1", "cookie2" ] }, the items() method returns
    the two pairs ("Set-Cookie", "cookie1") and ("Set-Cookie", "cookie2").
    This is convenient for most use cases. The only drawback is that
    len(keys()) is not equal to len(items()) for this specialized dict.
    """

    def elements(self, key):
        """Return a sorted list of HeaderElements for the given header."""
        return header_elements(key, self.get(key))

    def get_all(self, name):
        """Return a list of all the values for the named field."""
        value = self.get(name, '')
        if isinstance(value, list):
            return value
        return [val.strip() for val in value.split(',')]

    def __repr__(self):
        return "Headers(%s)" % repr(list(self.items()))

    def __str__(self):
        headers = ["%s: %s\r\n" % (k, v) for k, v in self.items()]
        return "".join(headers) + '\r\n'

    def items(self):
        for k, v in super(Headers, self).items():
            if isinstance(v, list):
                for vv in v:
                    yield (str(k), str(vv))
            else:
                yield (str(k), str(v))

    def __bytes__(self):
        return str(self).encode("latin1")

    def append(self, key, value):
        """
        If a header with the given name already exists, the value is
        normally appended to the existing value separated by a comma.

        If, however, the already existing entry associated key with a
        value of type list (as is the case for "Set-Cookie"),
        the new value is appended to that list.
        """
        if key not in self:
            if key.lower() == "set-cookie":
                self[key] = [value]
            else:
                self[key] = value
        else:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = ", ".join([self[key], value])

    def add_header(self, _name, _value, **_params):
        """Extended header setting.

        _name is the header field to add. keyword arguments can be used to set
        additional parameters for the header field, with underscores converted
        to dashes. Normally the parameter will be added as key="value" unless
        value is None, in which case only the key will be added.

        Example:

        h.add_header('content-disposition', 'attachment', filename='bud.gif')

        Note that unlike the corresponding 'email.Message' method, this does
        *not* handle '(charset, language, value)' tuples: all values must be
        strings or None.
        """
        parts = []
        if _value is not None:
            parts.append(_value)
        for k, v in list(_params.items()):
            k = k.replace('_', '-')
            if v is None:
                parts.append(k)
            else:
                parts.append(_formatparam(k, v))
        self.append(_name, "; ".join(parts))
