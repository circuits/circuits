"""Session Components

This module implements Session Components that can be used to store
and access persistent information.
"""


from uuid import uuid4 as uuid
from hashlib import sha1 as sha
from collections import defaultdict


from circuits import handler, Component


def who(request, encoding="utf-8"):
    """Create a SHA1 Hash of the User's IP Address and User-Agent"""

    ip = request.remote.ip
    agent = request.headers.get("User-Agent", "")

    return sha("{0:s}{1:s}".format(ip, agent).encode(encoding)).hexdigest()


def create_session(request):
    """Create a unique session id from the request

    Returns a unique session using ``uuid4()`` and a ``sha1()`` hash
    of the users IP Address and User Agent in the form of ``sid/who``.
    """

    return "{0:s}/{1:s}".format(uuid().hex, who(request))


def verify_session(request, sid):
    """Verify a User's Session

    This verifies the User's Session by verifying the SHA1 Hash
    of the User's IP Address and User-Agent match the provided
    Session ID.
    """

    if "/" not in sid:
        return create_session(request)

    user = sid.split("/", 1)[1]

    if user != who(request):
        return create_session(request)

    return sid


class Sessions(Component):

    channel = "web"

    def __init__(self, name="circuits.session", channel=channel):
        super(Sessions, self).__init__(channel=channel)

        self._name = name
        self._data = defaultdict(dict)

    def load(self, sid):
        return self._data[sid]

    def save(self, sid, data):
        """Save User Session Data for sid"""

    @handler("request", priority=10)
    def request(self, request, response):
        if self._name in request.cookie:
            sid = request.cookie[self._name].value
            sid = verify_session(request, sid)
        else:
            sid = create_session(request)

        request.sid = sid
        request.session = self.load(sid)
        response.cookie[self._name] = sid
