# Module:   ann
# Date:     18th March 2006
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Artificial Neural Networking Library

...
"""

import math
from time import time, sleep

from circuits.workers import Thread
from circuits import listener, Event

class Signal(Event): pass

class Node(Thread):

   def __init__(self, *args, **kwargs):
      super(Node, self).__init__(*args, **kwargs)

      self.start()

   def __repr__(self):
      return "<Node running=%s>" % self.running

   def fire(self, level=1.0):
      self.push(Signal(level), "signal")

   def run(self):
      while self.running:
         self.flush()
         sleep(0.01)

class Connection(Node):

   def __init__(self, *args, **kwargs):
      super(Connection, self).__init__(*args, **kwargs)

      self.weight = kwargs.get("weight", 1.0)

   def __repr__(self):
      return "<Connection weight=%0.2f>" % self.weight

   @listener("signal")
   def onSIGNAL(self, level):
      self.fire(level * self.weight)

class _StepNeuron(object):

   def compute(self):
      if self.level >= self.threshold:
         self.fire(1.0)
      else:
         self.fire(0.0)


class _LinearNeuron(object):

   def compute(self):
      self.fire(self.level + self.threshold)


class _SigmoidNeuron(object):

   def compute(self):
      self.fire(
            1.0 / (
               1.0 + math.exp(-1 * (
                  self.level + self.threshold)
                  )
               )
            )


class Neuron(Node):

   def __init__(self, *args, **kwargs):
      self.ls = None
      super(Neuron, self).__init__(*args, **kwargs)

      self.threshold = kwargs.get("threshold", 1.0)
      self.level = 0.0

      type = kwargs.get("type", "step")

      if type == "step":
         self.type = "Step"
         base = _StepNeuron
      elif type == "linear":
         self.type = "Linear"
         base = _LinearNeuron
      elif type == "sigmoid":
         self.type = "Sigmoid"
         base = _SigmoidNeuron
      else:
         raise TypeError("Invalid type")

      self.__class__.__bases__ += (base,)

   def __repr__(self):
      return "<Neuron type=%s threshold=%0.2f level=%0.2f>" % (
            self.type, self.threshold, self.level)

   @listener("signal")
   def onSIGNAL(self, level):
      self.ls = time()
      self.level += level

   def run(self):
      while self.running:
         if self.ls is not None and (time() - self.ls > 0.01):
            self.compute()
            self.level = 0.0
            self.ls = None
         self.flush()
         sleep(0.01)

class Output(Node):

   def __init__(self, *args, **kwargs):
      super(Output, self).__init__(*args, **kwargs)

      self.output = 0.0

   def __repr__(self):
      return "<Output output=%0.2f>" % self.output

   @listener("signal")
   def onSIGNAL(self, level):
      self.output = level
