
import pygame
from pygame import fastevent as event

from circuits.core import Event, Component

class KeyEvent(Event): pass
class QuitEvent(Event): pass
class FocusEvent(Event): pass
class MouseEvent(Event): pass
class ClickEvent(Event): pass
    
class PyGamePump(Component):

    def __init__(self, *args, **kwargs):
        super(PyGamePump, self).__init__(*args, **kwargs)

        pygame.init()
        event.init()

    def poll(self):
        for e in event.get():
            if e.type == pygame.QUIT:
                self.push(QuitEvent(), "quit")
            elif e.type == pygame.KEYDOWN:
                self.push(KeyEvent(e.key, e.mod), "keydown")
            elif e.type == pygame.KEYUP:
                self.push(KeyEvent(e.key, e.mod), "keyup")
            elif e.type == pygame.ACTIVEEVENT:
                self.push(FocusEvent(e.state, e.gain), "focus")
            elif e.type == pygame.MOUSEMOTION:
                self.push(MouseEvent(e.buttons, e.pos, e.rel), "mouse")
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.push(ClickEvent(e.button, e.pos), "click")
            elif e.type == pygame.MOUSEBUTTONUP:
                self.push(ClickEvent(e.button, e.pos), "click")
