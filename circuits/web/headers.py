"""
Headers Support

This module implements support for parsing and handling headers.
"""

import httoop
from httoop.header.element import HeaderElement


# monkey patch for backwards compatibility
httoop.header.element._AcceptElement.qvalue = property(lambda self: self.quality)


class Headers(httoop.Headers):
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

    def get_all(self, name):
        """Return a list of all the values for the named field."""
        fieldvalue = self.getbytes(name)
        if not fieldvalue:
            return []
        Element = httoop.header.element.HEADER.get(name, HeaderElement)
        return Element.split(fieldvalue)

    def add_header(self, _name, _value, **_params):
        """
        Extended header setting.

        _name is the header field to add. keyword arguments can be used to set
        additional parameters for the header field, with underscores converted
        to dashes. Normally the parameter will be added as key="value" unless
        value is None, in which case only the key will be added.

        Example:
        -------
        h.add_header('content-disposition', 'attachment', filename='bud.gif')

        Note that unlike the corresponding 'email.Message' method, this does
        *not* handle '(charset, language, value)' tuples: all values must be
        strings or None.

        """
        return self.append(_name, _value, **_params)
