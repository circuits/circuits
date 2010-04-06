Event Feedback
==============

Within the core of circuits is a feature called **Event Feedback**. This is a
mechanism that ties into any **Event** object allowing feedback to be given
for a number of criteria:
* **success**: An optional channel to use for Event Handler success
* **failure**: An optional channel to use for Event Handler failure
* **filter**: An optional channel to use if an Event is filtered
* **start**: An optional channel to use before an Event starts
* **end**: An optional channel to use when an Event ends

These criterion are specified on the **Event** class as class or instance
attributes and used to trigger an event on the channel specified in the form
of a 2-item tuple: ``(channel, target)``

To demonstrate just one of these **Event Feedback** channels, let's take the :download:`helloworld.py <../examples/helloworld.py>` example and modify it a bit to cascade some feedback on the ``Hello`` Event being fired:

.. literalinclude:: ../examples/helloworld.py
   :language: python
   :linenos:

Replace the ``Hello`` Event in L5-6 with::

   class Hello(Event):
      """Hello Event (with feedback)"""

      end = "goodbye",

Note:
 * Event Feedback channels must be 2-item tuples. The 2nd item (**target**) can be omitted.

Now let's create a new Event Handler for the feedback channel we just defined. Insert the following code above L17::

   def goodbye(self, e, handler, v):
      print "Goodbye World!"
      print "Event:", e
      print "Handler:", handler
      print "Return Value:", v
      raise SystemExit, 0

Let's also modify our orignal ``Hello`` Event Handler so we don't terminate the system with a ``SystemExit`` Exception raised here, instead we'll do this in our Event Feedback's Event Handler (*above*)::

   def hello(self):
      print "Hello World!"

Note:
 * It's important that any Event Handler for Event Feedback channel(s) adhere and define the correct signature (*parameters*). ``end`` feedback for example requires 3 parameters: ``(e, handler, v)``
 * **DO NOT** name the 1st parameter ``event`` as this has a special meaning in any Event Handlers in circuits.
 * See: ... for more information.

When this modified example is run, here's the output you'll expect:

.. code-block:: bash

   $ python source/examples/helloworld.py 
   Hello World!
   Goodbye World!
   Event: <Hello[*:hello] [] {}>
   Handler <bound method App.hello of <App/* (queued=0, channels=3, handlers=3) [R]>>
   Return Value: None

