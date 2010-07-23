# Module:   sessions
# Date:     22nd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Session Components

This module implements Session Components that can be used to store
and access persistent information.
"""

from uuid import uuid4 as uuid
from collections import defaultdict

from circuits import handler, Component

class Sessions(Component):

    channel = "web"

    def __init__(self, name="circuits.session", *args, **kwargs):
        super(Sessions, self).__init__(*args, **kwargs)

        self._name = name
        self._data = defaultdict(dict)

    def _load(self, id):
        return self._data[id]

    def _save(self, id, data):
        self._data[id] = data

    @handler("request", filter=True, priority=10)
    def request(self, request, response):
        if self._name in request.cookie:
            id = request.cookie[self._name].value
        else:
            id = str(uuid())

        request.sid = id
        request.session = self._load(id)
        response.cookie[self._name] = id
