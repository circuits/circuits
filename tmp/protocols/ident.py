# Module:   ident
# Date:     6th March 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Identification Protocol (RFC 1413)

The Identification Protocol (a.k.a., "ident", a.k.a., "the Ident
rotocol") provides a means to determine the identity of a user of a
articular TCP connection.  Given a TCP port number pair, it returns
 character string which identifies the owner of that connection on
he server's system.
"""

from circuits.core import handler, Event, BaseComponent

class Ident(BaseComponent):

    channel = "ident"

    def __init__(self, *args, **kwargs):
        super(Ident, self).__init__(*args, **kwargs)

