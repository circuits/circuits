"""
.. codeauthor: mnl
"""
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
from threading import Event
from time import time

class FallBackGenerator(BaseComponent):
    
    def __init__(self, *args, **kwargs):
        super(FallBackGenerator, self).__init__(*args, **kwargs)
        self._continue = Event()
    
    @handler("generate_events", priority=-100, filter=True)
    def _on_generate_events(self, event):
        """
        Fall back handler for the :class:`~.events.GenerateEvents` event.
        """
        with event.lock:
            if event.time_left == 0:
                return True
            self._continue.clear()

        while event.time_left < 0 and not self._continue.is_set():
            # If we get here, there was no work left to do when creating
            # the GenerateEvents event and there is no other handler that is
            # prepared to supply new events within a limited time. The
            # application will continue only if some other Thread fires
            # an event.
            #
            # Python ignores signals when waiting without timeout. 
            self._continue.wait(10000)            
        while event.time_left > 0 and not self._continue.is_set():
            start_time = time()
            self._continue.wait(event.time_left)
            time_spent = time() - start_time
            event.reduce_time_left(max(event.time_left - time_spent, 0))
        return True

    def resume(self):
        """
        Implements the resume method as required from components that
        handle :class:`~.events.GenerateEvents`.
        """
        self._continue.set()
                