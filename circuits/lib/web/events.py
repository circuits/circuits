# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event

class Request(Event):
    """Request(Event) -> Request Event

    args: request, response
    """

class Response(Event):
    """Response(Event) -> Response Event

    args: request, response
    """

class Stream(Event):
    """Stream(Event) -> Stream Event

    args: request, response
    """

class Write(Event):
    """Write(Event) -> Write Event

    args: sock
    """

class Close(Event):
    """Close(Event) -> Close Event

    args: sock
    """
