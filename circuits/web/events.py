# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event


class webevent(Event):
    """
    webevents have both their ``success`` and ``failure`` attributes set to
    True. So event processing generates the derived events
    ``...Success`` or ``...Failure`` events.
    """

    success = True
    failure = True
    complete = True


class request(webevent):
    """request(eebEvent) -> request webevent

    args: request, response
    """


class response(webevent):
    """response(webevent) -> response webevent

    args: request, response
    """


class stream(webevent):
    """stream(webevent) -> stream webevent

    args: request, response
    """
