#!/usr/bin/env python

import pygame
from pygame import K_q
from pygame import DOUBLEBUF, HWSURFACE

from circuits import Component, Debugger
from circuits.drivers._pygame import PyGameDriver

class Test(Component):

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        pygame.init()
        self += PyGameDriver() + Debugger()
        screen = pygame.display.set_mode((640, 480), DOUBLEBUF | HWSURFACE)

    def keyup(self, key, mod):
        if key == K_q:
            raise SystemExit, 0

    def quit(self):
        raise SystemExit, 0

Test().run()
