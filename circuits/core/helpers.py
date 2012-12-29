"""
.. codeauthor: mnl
"""
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
from threading import Event


class FallBackGenerator(BaseComponent):

    def __init__(self, *args, **kwargs):
        super(FallBackGenerator, self).__init__(*args, **kwargs)
        self._continue = Event()

    @handler("generate_events", priority=-100, filter=True)
    def _on_generate_events(self, event):
        """
        Fall back handler for the :class:`~.events.GenerateEvents` event.
        """
        while event.time_left < 0:
            # If we get here, there was no work left to do when creating
            # the GenerateEvents event and there is no other handler that is
            # prepared to supply new events within a limited time. The
            # application will continue only if some other Thread fires
            # an event.
            #
            # Python ignores signals when waiting without timeout.
            self.root.needs_resume = self.resume
            self._continue.wait(10000)
            if self._continue.is_set():
                self._continue.clear()
                self.root.needs_resume = None
                break

        while event.time_left > 0:
            self.root.needs_resume = self.resume
            self._continue.wait(event.time_left)
            if self._continue.is_set():
                self._continue.clear()
                self.root.needs_resume = None
                break

        return True

    def resume(self):
        """
        Implements the resume method as required from components that
        handle :class:`~.events.GenerateEvents`.
        """
        self._continue.set()
