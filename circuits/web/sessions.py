"""Session Components

This module implements Session Components that can be used to store
and access persistent information.
"""
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from hashlib import sha1 as sha
from uuid import uuid4 as uuid

from circuits import Component, handler
from circuits.six import with_metaclass


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


class Session(dict):

    def __init__(self, sid, data, store):
        super(Session, self).__init__(data)

        self._sid = sid
        self._store = store

    @property
    def sid(self):
        return self._sid

    @property
    def store(self):
        return self._store

    def expire(self):
        self.store.delete(self.sid)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.store.save(self.sid, self)


class Store(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def delete(self, sid):
        """Delete the session data identified by sid"""

    @abstractmethod
    def load(self, sid):
        """Load the session data identified by sid"""

    @abstractmethod
    def save(self, sid):
        """Save the session data identified by sid"""


class MemoryStore(Store):

    def __init__(self):
        self._data = defaultdict(dict)

    @property
    def data(self):
        return self._data

    def delete(self, sid):
        del self.data[sid]

    def load(self, sid):
        return Session(sid, self.data[sid], self)

    def save(self, sid, data):
        self.data[sid] = data


class Sessions(Component):

    channel = "web"

    def __init__(self, name="circuits", store=MemoryStore, channel=channel):
        super(Sessions, self).__init__(channel=channel)

        self._name = name
        self._store = store()

    @property
    def name(self):
        return self._name

    @property
    def store(self):
        return self._store

    @handler("request", priority=10)
    def request(self, request, response):
        if self.name in request.cookie:
            sid = request.cookie[self._name].value
            sid = verify_session(request, sid)
        else:
            sid = create_session(request)

        request.session = self.store.load(sid)
        response.cookie[self.name] = sid
