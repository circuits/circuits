# Module:   ann
# Date:     18th March 2006
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Artificial Neural Networking Library

...
"""

import math
from time import sleep

from circuits import Event, Component

class Signal(Event): pass

class Node(Component):

   def __init__(self, *args, **kwargs):
      super(Node, self).__init__(*args, **kwargs)

      self.start()

   def __repr__(self):
      return "<Node (%d) running=%s>" % (id(self), self.running)

   def fire(self, level=1.0):
      self.push(Signal(level), "signal", self.channel)

class Synapse(Node):

   def __init__(self, *args, **kwargs):
      super(Synapse, self).__init__(*args, **kwargs)

      self.weight = kwargs.get("weight", 1.0)

   def __repr__(self):
      return "<Synapse (%d) weight=%0.2f>" % (id(self), self.weight)

   def signal(self, level):
      self.fire(level * self.weight)

class Neuron(Node):

   def __init__(self, *args, **kwargs):
      super(Neuron, self).__init__(*args, **kwargs)

      self.threshold = kwargs.get("threshold", 1.0)
      self.level = 0.0

      self.type = kwargs.get("type", "step")
      self._compute = getattr(self, "_%s" % self.type)

   _compute = lambda self: None

   def __tick__(self):
      sleep(0.1)
      self._compute()
      self.level = 0.0

   def _step(self):
      if self.level >= self.threshold:
         self.fire(1.0)
      else:
         self.fire(0.0)

   def _linear(self):
      self.fire(self.level + self.threshold)

   def _sigmoid(self):
      self.fire(
            1.0 / (
               1.0 + math.exp(-1 * (
                  self.level + self.threshold)
                  )
               )
            )

   def __repr__(self):
      return "<Neuron (%d) type=%s threshold=%0.2f level=%0.2f>" % (
            id(self), self.type, self.threshold, self.level)

   def signal(self, level):
      self.level += level

class Output(Node):

   def __init__(self, *args, **kwargs):
      super(Output, self).__init__(*args, **kwargs)

      self.output = 0.0

   def __repr__(self):
      return "<Output (%d) output=%0.2f>" % (id(self), self.output)

   def signal(self, level):
      self.output = level
