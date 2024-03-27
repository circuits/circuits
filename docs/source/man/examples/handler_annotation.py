#!/usr/bin/env python

from circuits import BaseComponent, Debugger, handler


class MyComponent(BaseComponent):
    def __init__(self) -> None:
        super().__init__()

        Debugger().register(self)

    @handler('started', channel='*')
    def system_started(self, component) -> None:
        print('Start event detected')


MyComponent().run()
