# Module:   pygame_driver
# Date:     1st February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""PyGame Driver

A driver for the pygame library.
"""

from circuits.core import Event, Component
from circuits.lib.drivers import DriverError

class KeyEvent(Event): pass
class QuitEvent(Event): pass
class FocusEvent(Event): pass
class MouseEvent(Event): pass
class ClickEvent(Event): pass
    
class PyGameDriver(Component):

    def __new__(cls, *args, **kwargs):
        try:
            import pygame
            from pygame import fastevent as event
        except ImportError:
            raise DriverError("No pygame support available.")

        self = super(PyGameDriver, cls).__new__(*args, **kwargs)

        self.pygame = pygame
        self.event = event

        self.pygame.init()
        self.event.init()

        return self

    def poll(self):
        for e in self.event.get():
            if e.type == self.pygame.QUIT:
                self.push(QuitEvent(), "quit")
            elif e.type == self.pygame.KEYDOWN:
                self.push(KeyEvent(e.key, e.mod), "keydown")
            elif e.type == self.pygame.KEYUP:
                self.push(KeyEvent(e.key, e.mod), "keyup")
            elif e.type == self.pygame.ACTIVEEVENT:
                self.push(FocusEvent(e.state, e.gain), "focus")
            elif e.type == self.pygame.MOUSEMOTION:
                self.push(MouseEvent(e.buttons, e.pos, e.rel), "mouse")
            elif e.type == self.pygame.MOUSEBUTTONDOWN:
                self.push(ClickEvent(e.button, e.pos), "click")
            elif e.type == self.pygame.MOUSEBUTTONUP:
                self.push(ClickEvent(e.button, e.pos), "click")
