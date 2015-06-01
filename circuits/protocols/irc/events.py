"""Internet Relay Chat Protocol events"""


from circuits import Event


class response(Event):

    """response Event (Server and Client)"""


class reply(Event):

    """reply Event (Server)"""


class request(Event):

    """request Event (Client)"""
