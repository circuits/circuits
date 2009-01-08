# Module:   ann
# Date:     18th March 2006
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Artificial Neural Networking Library

...
"""

import math
from time import time, sleep

from circuits import listener, Event, Thread


class SignalEvent(Event): pass


class Node(Thread):

   def __init__(self, *args, **kwargs):
      super(Node, self).__init__(*args, **kwargs)

      self._inputs = []

   def __repr__(self):
      return "<Node running=%s>" % self.isRunning()

   def _getInputs(self):
      return self._inputs

   def link(self, node):
      Worker.link(self, node)
      node._inputs.append(self)

   def fire(self, level=1.0):
      self.event.push(SignalEvent(self, level), "signal")

   def run(self):
      while self.isRunning():
         self.flush()
         sleep(0.01)

   inputs = property(_getInputs)


def new_node(*args, **kwargs):

   class NewNode(Node):
      pass
   return NewNode(*args, **kwargs)


class Connection(Node):

   def __init__(self, *args, **kwargs):
      super(Connection, self).__init__(*args, **kwargs)

      self._weight = kwargs.get("weight", 1.0)

   def __repr__(self):
      return "<Connection weight=%0.2f>" % self._weight

   def _get_weight(self):
      try:
         return self._weight
      except:
         return None

   def _set_weight(self, weight):
      self._weight = weight

   @listener("signal")
   def onSIGNAL(self, source, level):
      self.fire(level * self._weight)

   weight = property(_get_weight, _set_weight)


def new_connection(*args, **kwargs):

   class NewConnection(Connection):
      pass
   return NewConnection(*args, **kwargs)


class _StepNeuron(object):

   def compute(self):
      if self._level >= self._threshold:
         self.fire(1.0)
      else:
         self.fire(0.0)


class _LinearNeuron(object):

   def compute(self):
      self.fire(self._level + self._threshold)


class _SigmoidNeuron(object):

   def compute(self):
      self.fire(
            1.0 / (
               1.0 + math.exp(-1 * (
                  self._level + self._threshold)
                  )
               )
            )


class Neuron(Node):

   def __init__(self, *args, **kwargs):
      super(Neuron, self).__init__(*args, **kwargs)

      self._threshold = threshold
      self._level = 0.0
      self._ls = None

      if type == "step":
         self._type = "Step"
         base = _StepNeuron
      elif type == "linear":
         self._type = "Linear"
         base = _LinearNeuron
      elif type == "sigmoid":
         self._type = "Sigmoid"
         base = _SigmoidNeuron
      else:
         raise TypeError("Invalid type")

      self.__class__.__bases__ += (base,)

   def __repr__(self):
      return "<Neuron type=%s threshold=%0.2f level=%0.2f>" % (
            self._type, self._threshold, self._level)

   def _get_threshold(self):
      try:
         return self._threshold
      except:
         return None

   def _set_threshold(self, threshold):
      self._threshold = threshold

   @listener("signal")
   def onSIGNAL(self, source, level):
      self._ls = time()
      self._level += level

   def run(self):
      while self.isRunning():
         if self._ls is not None and (time() - self._ls > 0.01):
            self.compute()
            self._level = 0.0
            self._ls = None
         self.event.flush()
         sleep(0.01)

   threshold = property(_get_threshold, _set_threshold)

def new_neuron(*args, **kwargs):
   class NewNeuron(Neuron):
      pass
   return NewNeuron(*args, **kwargs)


class Output(Node):

   def __init__(self, *args, **kwargs):
      super(Output, self).__init__(*args, **kwargs)

      self._f = f
      self._output = None

   def _getOutput(self):
      return self._output

   @listener("signal")
   def onSIGNAL(self, source, level):
      self._output = level
      self._f(self)

   output = property(_getOutput)

def new_output(*args, **kwargs):
   class NewOutput(Output):
      pass
   return NewOutput(*args, **kwargs)
