# -*- coding: utf-8 -*-
""" Circuits events for STOMP Client """

import logging

from circuits import Event

LOG = logging.getLogger(__name__)


class stomp_event(Event):
    """A Circuits event with less verbose repr"""
    success = True

    def _repr(self):
        return ""

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        if len(self.channels) > 1:
            channels = repr(self.channels)
        elif len(self.channels) == 1:
            channels = str(self.channels[0])
        else:
            channels = ""

        data = self._repr()

        return u"<%s[%s] (%s)>" % (self.name, channels, data)


class disconnected(stomp_event):
    def __init__(self, reconnect=True, receipt=None):
        super(disconnected, self).__init__(receipt=receipt)
        self.reconnect = reconnect


class disconnect(stomp_event):
    pass


class message(stomp_event):
    def __init__(self, frame):
        super(message, self).__init__(headers=frame.headers,
                                      message=frame.body)
        self.frame = frame


class send(stomp_event):
    def __init__(self, headers, body, destination):
        super(send, self).__init__(headers=headers,
                                   body=body,
                                   destination=destination)


class client_heartbeat(stomp_event):
    pass


class server_heartbeat(stomp_event):
    pass


class connect(stomp_event):
    def __init__(self, subscribe=False, host=None):
        super(connect, self).__init__(host=host)
        self.subscribe = subscribe


class connected(stomp_event):
    pass


class connection_failed(stomp_event):
    reconnect = True


class on_stomp_error(stomp_event):
    def __init__(self, frame, err):
        headers = frame.headers if frame else {}
        body = frame.body if frame else None
        super(on_stomp_error, self).__init__(headers=headers,
                                             message=body,
                                             error=err)
        self.frame = frame


class heartbeat_timeout(stomp_event):
    pass


class subscribe(stomp_event):
    def __init__(self, destination, **kwargs):
        super(subscribe, self).__init__(destination=destination, **kwargs)
        self.destination = destination


class unsubscribe(stomp_event):
    def __init__(self, destination):
        super(unsubscribe, self).__init__(destination=destination)
        self.destination = destination


class ack(stomp_event):
    def __init__(self, frame):
        super(ack, self).__init__(frame=frame)
        self.frame = frame
