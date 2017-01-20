"""Internet Relay Chat Protocol"""


from re import compile as compile_regex

from circuits import Component
from circuits.net.events import write
from circuits.protocols.line import Line

from .commands import PONG
from .events import response
from .utils import parsemsg

NUMERIC = compile_regex("[0-9]+")


class IRC(Component):

    """IRC Protocol Component

    Creates a new IRC Component instance that implements the IRC Protocol.
    Incoming messages are handled by the "read" Event Handler, parsed and
    processed with appropriate Events created and exposed to the rest of
    the system to listen to and handle.
    """

    def __init__(self, *args, **kwargs):
        super(IRC, self).__init__(*args, **kwargs)

        self.encoding = kwargs.get("encoding", "utf-8")

        Line(**kwargs).register(self)

    def line(self, *args):
        """line Event Handler

        Process a line of text and generate the appropriate
        event. This must not be overridden by subclasses,
        if it is, this must be explicitly called by the
        subclass. Other Components may however listen to
        this event and process custom IRC events.
        """

        if len(args) == 1:
            # Client read
            sock, line = None, args[0]
        else:
            # Server read
            sock, line = args

        prefix, command, args = parsemsg(line, encoding=self.encoding)

        command = command.lower()

        if NUMERIC.match(command):
            args.insert(0, int(command))
            command = "numeric"

        if sock is not None:
            self.fire(response.create(command, sock, prefix, *args))
        else:
            self.fire(response.create(command, prefix, *args))

    def request(self, event, message):
        """request Event Handler (Default)

        This is a default event handler to respond to ``request`` events
        by converting the given message to bytes and firing a ``write``
        event to a hopefully connected client socket.
        Components may override this, but be sure to respond to
        ``request`` events by either explicitly calling this method
        or sending your own ``write`` events as the client socket.
        """

        event.stop()
        message.encoding = self.encoding
        self.fire(write(bytes(message)))

    def ping(self, event, *args):
        """ping Event Handler (Default)

        This is a default event to respond to ``ping`` events
        by sending a ``PONG`` in response. Subclasses or
        components may override this, but be sure to respond to
        ``ping`` events by either explicitly calling this method
        or sending your own ``PONG`` response.
        """

        if len(args) == 2:
            # Client read
            self.fire(PONG(args[1]))
            event.stop()
