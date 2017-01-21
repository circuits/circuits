"""
.. codeauthor: mnl
"""
from signal import SIGINT, SIGTERM
from sys import stderr
from threading import Event
from traceback import format_exception_only

from circuits.core.handlers import reprhandler

from .components import BaseComponent
from .handlers import handler


class FallBackGenerator(BaseComponent):

    def __init__(self, *args, **kwargs):
        super(FallBackGenerator, self).__init__(*args, **kwargs)
        self._continue = Event()

    @handler("generate_events", priority=-100)
    def _on_generate_events(self, event):
        """
        Fall back handler for the :class:`~.events.GenerateEvents` event.

        When the queue is empty a GenerateEvents event is fired, here
        we sleep for as long as possible to avoid using extra cpu cycles.

        A poller would override this with a higher priority handler.
        e.g: ``@handler("generate_events", priority=0)``
        and provide a different way to idle when the queue is empty.
        """

        with event.lock:
            if event.time_left == 0:
                event.stop()
            self._continue.clear()

        if event.time_left > 0:
            # If we get here, there is no component with work to be
            # done and no new event. But some component has requested
            # to be checked again after a certain timeout.
            self._continue.wait(event.time_left)
            # Either time is over or _continue has been set, which
            # implies resume has been called, which means that
            # reduce_time_left(0) has been called. So calling this
            # here is OK in any case.
            event.reduce_time_left(0)
            event.stop()

        while event.time_left < 0:
            # If we get here, there was no work left to do when creating
            # the GenerateEvents event and there is no other handler that
            # is prepared to supply new events within a limited time. The
            # application will continue only if some other Thread fires
            # an event.
            #
            # Python ignores signals when waiting without timeout.
            self._continue.wait(10000)

        event.stop()

    def resume(self):
        """
        Implements the resume method as required from components that
        handle :class:`~.events.GenerateEvents`.
        """
        self._continue.set()


class FallBackExceptionHandler(BaseComponent):

    """
    If there is no handler for error events in the component hierarchy, this
    component's handler is added automatically. It simply prints
    the error information on stderr.
    """

    @handler("exception", channel="*")
    def _on_exception(self, error_type, value, traceback,
                      handler=None, fevent=None):
        s = []

        if handler is None:
            handler = ""
        else:
            handler = reprhandler(handler)

        msg = "ERROR {0:s} ({1:s}) ({2:s}): {3:s}\n".format(
            handler, repr(fevent), repr(error_type), repr(value)
        )

        s.append(msg)
        s.append('Traceback (most recent call last):\n')
        s.extend(traceback)
        s.extend(format_exception_only(error_type, value))
        s.append("\n")
        stderr.write("".join(s))


class FallBackSignalHandler(BaseComponent):

    """
    If there is no handler for signal events in the component hierarchy, this
    component's handler is added automatically. It simply terminates the
    system if the signal is SIGINT or SIGTERM.
    """

    @handler("signal", channel="*")
    def _on_signal(self, signo, stack):
        if signo in [SIGINT, SIGTERM]:
            raise SystemExit(0)
