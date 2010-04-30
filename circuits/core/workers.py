#!/usr/bin/env python

from threading import Thread as _Thread

try:
    from multiprocessing import Value as _Value
    from multiprocessing import Process as _Process
    from multiprocessing.sharedctypes import Synchronized as _Synchronized
    HAS_MULTIPROCESSING = 2
except:
    try:
        from processing import Value as _Value
        from processing import Process as _Process
        from processing.sharedctypes import Synchronized as _Synchronized
        HAS_MULTIPROCESSING = 1
    except:
        HAS_MULTIPROCESSING = 0

from bridge import Bridge
from utils import findroot
from manager import Manager
from components import BaseComponent as _BaseComponent

from circuits.net.sockets import Pipe

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
        return self._running and self._thread.isAlive()

class Process(_BaseComponent):

    def __init__(self, manager=None, **kwargs):
        channel = kwargs.get("channel", Process.channel)
        super(Process, self).__init__(channel=channel)

        self._manager = manager

        self._bridge = None

        self._running = _Value("b", False)

    def __main__(self, running, socket=None):
        if socket is not None:
            manager = Manager()
            bridge = Bridge(manager, socket=socket)
            self.register(manager)
            manager.start()

        try:
            self.run()
        finally:
            if socket is not None:
                while bridge or manager: pass
                manager.stop()
                bridge.stop()

    def start(self):
        args = (self._running,)

        if self._manager is not None:
            root = findroot(self._manager)
            parent, child = Pipe()
            self._bridge = Bridge(root, socket=parent)
            self._bridge.start()

            args = (self._running, child,)

        self._process = _Process(target=self.__main__, args=args)
        self._process.daemon = True
        if HAS_MULTIPROCESSING == 2:
            setattr(self._process, "isAlive", self._process.is_alive)

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
        return hasattr(self, "_process") and self._process.join()

    @property
    def alive(self):
        if type(self._running) is _Synchronized:
            return self._running.value and self._process.isAlive()

if not HAS_MULTIPROCESSING:
    Process = Thread
