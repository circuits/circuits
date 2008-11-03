.. highlight:: python

Quickstart
==========

:Status: Work in progress

.. contents:: Table of Contents
    :depth: 2

Now that you've got Circuits installed, what now ?

The very first thing you'll need to do is import parts of the circuits library:
   >>> from circuits import listener, Event, Component, Manager

The Pattern
-----------

A recommended pattern for circuits based systems/application is as follows:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   from traceback import format_exc

   from circuits import listener, Event, Component, Manager

   ###
   ### Events
   ###

   class Foo(Event):
      "Foo Event"

   class Bar(Event):
      "Bar Event"

   ###
   ### Components
   ###

   class FooBar(Component):

      @listener("foo")
      def onFOO(self):
         print "foo"

      @listener("bar")
      def onBAR(self):
         print "bar"

   ###
   ### Main
   ###

   def main():
      manager = Manager()

      foobar = FooBar()

      manager += foobar

      manager.push(Foo(), "foo")
      manager.push(Bar(), "bar")

      while True:
         try:
            manager.flush()
         except KeyboardInterrupt:
            break
         except Exception, error:
            print "ERROR: %s" % error
            print format_exc()

   ###
   ### Entry Point
   ###

   if __name__ == "__main__":
      main()

