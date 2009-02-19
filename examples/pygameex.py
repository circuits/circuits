#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

import pygame
from pygame import K_q
from pygame import DOUBLEBUF, HWSURFACE

from circuits.drivers import PyGameDriver
from circuits import Component, Debugger, Manager

class Test(Component):

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)

        screen = pygame.display.set_mode((640, 480), DOUBLEBUF | HWSURFACE)

    def keyup(self, key, mod):
        if key == K_q:
            raise SystemExit, 0

    def quit(self):
        raise SystemExit, 0

def main():

    manager = Manager()
    manager += Debugger()

    driver = PyGameDriver()
    test = Test()

    manager += driver
    manager += test

    while True:
        try:
            driver.poll()
            manager.flush()
        except KeyboardInterrupt:
            break
        except SystemExit:
            break

if __name__ == "__main__":
    main()
