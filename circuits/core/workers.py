#!/usr/bin/env python

from threading import Thread as _Thread

try:
    from multiprocessing import Pipe as _Pipe
    from multiprocessing import Value as _Value
    from multiprocessing import Process as _Process
    from multiprocessing.sharedctypes import Synchronized

    HAS_MULTIPROCESSING = 2
except:
    try:
        from processing import Pipe as _Pipe
        from processing import Value as _Value
        from processing import Process as _Process
        from processing.sharedctypes import Synchronized

        HAS_MULTIPROCESSING = 1
    except:
        HAS_MULTIPROCESSING = 0


from components import BaseComponent as _BaseComponent

TIMEOUT = 0.2

class Thread(_BaseComponent):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)

        self._thread = _Thread(target=self.run)

    def start(self):
        self._running = True
        self._thread.start()

    def run(self):
        """To be implemented by subclasses"""

    def stop(self):
        self._running = False

    def join(self):
        return self._thread.join()

    @property
    def alive(self):
        return self.running and self._thread.isAlive()

if HAS_MULTIPROCESSING:

    class Process(_BaseComponent):

        def __init__(self, *args, **kwargs):
            super(Process, self).__init__(*args, **kwargs)

            self._running = _Value("b", False)
            self._timeout = kwargs.get("timeou", TIMEOUT)
            self._process = _Process(target=self._run,
                    args=(self.run, self._running,))
            self._parent, self._child = _Pipe()

        def __tick__(self):
            if self._parent.poll(self._timeout):
                event = self._parent.recv()
                channel = event.channel
                target = event.target
                self.push(event, channel, target)

        def _run(self, fn, running):
            thread = _Thread(target=fn)
            thread.start()

            try:
                while running.value and thread.isAlive():
                    try:
                        self.flush()
                        if self._child.poll(self._timeout):
                            event = self._child.recv()
                            channel = event.channel
                            target = event.target
                            self.push(event, channel, target)
                    except KeyboardInterrupt, SystemExit:
                        running.acquire()
                        running.value = False
                        running.release()
            finally:
                running.acquire()
                running.value = False
                running.release()
                self.flush()

        def start(self):
            self._running.acquire()
            self._running.value = True
            self._running.release()
            self._process.start()

        def run(self):
            """To be implemented by subclasses"""

        def stop(self):
            self._running.acquire()
            self._running.value = False
            self._running.release()

        def join(self):
            return self._process.join()

        @property
        def alive(self):
            if type(self._running) is Synchronized:
                return self._running.value and self._process.is_alive()

else:
    Process = Thread
