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

    def __init__(self, name="circuits.session", *args, **kwargs):
        super(Sessions, self).__init__(*args, **kwargs)

        self.name = name
        self.sessions = defaultdict(dict)

    @handler("request", filter=True)
    def request(self, request, response):
        if self.name in request.cookie:
            id = request.cookie[self.name].value
        else:
            id = str(uuid())

        request.session = self.sessions[id]
        response.cookie[self.name] = id
