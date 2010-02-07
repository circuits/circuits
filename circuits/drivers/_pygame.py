# Module:   pygame_driver
# Date:     1st February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""PyGame Driver

A driver for the pygame library.
"""

import pygame

try:
    from pygame import fastevent as event
except ImportError:
    from pygame import event
except ImportError:
    raise Exception("No pygame support available. Is pygame installed?")

from circuits.core import Event, Component

class Key(Event): pass
class Quit(Event): pass
class Focus(Event): pass
class Mouse(Event): pass
class ButtonDown(Event): pass
class ButtonUp(Event): pass
class Unknown(Event): pass
    
class PyGameDriver(Component):

    channel = "pygame"

    def __new__(cls, *args, **kwargs):
        self = super(PyGameDriver, cls).__new__(cls, *args, **kwargs)
        event.init()
        return self

    def __tick__(self):
        self.poll()

    def poll(self):
        for e in event.get():
            if e.type == pygame.QUIT:
                self.push(Quit(), "quit")
            elif e.type == pygame.KEYDOWN:
                self.push(Key(e.key, e.mod), "keydown")
            elif e.type == pygame.KEYUP:
                self.push(Key(e.key, e.mod), "keyup")
            elif e.type == pygame.ACTIVEEVENT:
                self.push(Focus(e.state, e.gain), "focus")
            elif e.type == pygame.MOUSEMOTION:
                self.push(Mouse(e.buttons, e.pos, e.rel), "mouse")
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.push(ButtonDown(e.button, e.pos), "buttondown")
            elif e.type == pygame.MOUSEBUTTONUP:
                self.push(ButtonUp(e.button, e.pos), "buttonup")
            else:
                self.push(Unknown(e), "unknown")
