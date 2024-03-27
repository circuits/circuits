#!/usr/bin/env python

from circuits import Component


class MyComponent(Component):
    def started(self, *args) -> None:
        print('Hello World!')


MyComponent().run()
