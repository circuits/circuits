#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

import pygame
from pygame import *

from circuits.lib.pygamepump import PyGamePump
from circuits import listener, Event, Component, Debugger, Manager

class Test(Component):

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)

        screen = pygame.display.set_mode((640, 480),    DOUBLEBUF | HWSURFACE)

    @listener("keyup")
    def onKEYUP(self, key, mod):
        if key == K_q:
            raise SystemExit, 0

    @listener("quit")
    def onQUIT(self):
        raise SystemExit, 0

def main():

    manager = Manager()
    manager += Debugger()

    pump = PyGamePump()
    test = Test()

    manager += pump
    manager += test

    while True:
        try:
            pump.poll()
            manager.flush()
        except KeyboardInterrupt:
            break
        except SystemExit:
            break

if __name__ == "__main__":
    main()
