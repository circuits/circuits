#!/usr/bin/env python

from threading import Thread as _Thread
from threading import enumerate as threads

try:
    from multiprocessing import Pipe as _Pipe
    from multiprocessing import Value as _Value
    from multiprocessing import Process as _Process

    from multiprocessing import cpu_count as cpus
    from multiprocessing import active_children as processes
    HAS_MULTIPROCESSING = 2
except:
    try:
        from processing import Pipe as _Pipe
        from processing import Value as _Value
        from processing import Process as _Process

        from processing import cpuCount as cpus
        from processing import activeChildren as processes
        HAS_MULTIPROCESSING = 1
    except:
        HAS_MULTIPROCESSING = 0


from circuits.core import BaseComponent as _BaseComponent

POLL_INTERVAL = 0.00001

class Thread(_BaseComponent):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)

        self._thread = _Thread(target=self.run)

    def start(self):
        self._running = True
        self._thread.start()

    def run(self):
        pass

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
            self.process = _Process(target=self._run, args=(self.run, self._running,))
            self.parent, self.child = _Pipe()

        def _run(self, fn, running):
            thread = _Thread(target=fn)
            thread.start()

            try:
                while running.value:
                    try:
                        self.flush()
                        if self.child.poll(POLL_INTERVAL):
                            event = self.child.recv()
                            channel = event.channel
                            target = event.target
                            self.send(event, channel, target)
                    except SystemExit:
                        running.acquire()
                        running.value = False
                        running.release()
                        break
                    except KeyboardInterrupt:
                        running.acquire()
                        running.value = False
                        running.release()
                        break
            finally:
                running.acquire()
                running.value = False
                running.release()
                thread.join()
                self.flush()

        def start(self):
            self._running.acquire()
            self._running.value = True
            self._running.release()
            self.process.start()

        def run(self):
            pass

        def stop(self):
            self._running.acquire()
            self._running.value = False
            self._running.release()

        def isAlive(self):
            return self._running.value

        def poll(self, wait=POLL_INTERVAL):
            if self.parent.poll(POLL_INTERVAL):
                event = self.parent.recv()
                channel = event.channel
                target = event.target
                self.send(event, channel, target)

else:
    Process = Thread
