Values
======


.. module:: circuits.core.values


The :mod:`~circuits.core` :class:`~Value`
class is an internal part of circuits'
`Futures and Promises <http://en.wikipedia.org/wiki/Futures_and_promises>`_
used to fulfill promises of the return value of
an event handler and any associated chains of
events and event handlers.

Basically when you fire an event ``foo()``
such as:

.. code-block:: python
    
    x = self.fire(foo())

``x`` here is an instance of the
:class:`~Value` class which will
contain the value returned by the
event handler for ``foo`` in
the ``.value`` property.

.. note:: There is also :meth:`~Value.getValue`
          which can be used to also retrieve the
          underlying value held in the instance
          of the :class:`~Value` class but you
          should not need to use this as the
          ``.value`` property takes care of this
          for you.

The only other API you may need in your application
is the :py:attr:`~Value.notify` which can be used
to trigger a ``value_changed`` event when the
underlying :class:`~Value` of the event handler has
changed. In this way you can do something asynchronously
with the event handler's return value no matter when
it finishes.

Example Code:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/python -i


    from circuits import handler, Event, Component, Debugger


    class hello(Event):
        "hello Event"


    class test(Event):
        "test Event"


    class App(Component):

        def hello(self):
            return "Hello World!"

        def test(self):
            return self.fire(hello())

        @handler("hello_value_changed")
        def _on_hello_value_changed(self, value):
            print("hello's return value was: {}".format(value))


    app = App()
    Debugger().register(app)

Example Session:

.. code-block:: python
    :linenos:
    
    $ python -i ../app.py 
    >>> x = app.fire(test())
    >>> x.notify = True
    >>> app.tick()
    <registered[*] (<Debugger/* 27798:MainThread (queued=0) [S]>, <App/* 27798:MainThread (queued=1) [S]> )>
    <test[*] ( )>
    >>> app.tick()
    <hello[*] ( )>
    >>> app.tick()
    <test_value_changed[<App/* 27798:MainThread (queued=0) [S]>] (<Value ('Hello World!') result=True; errors=False; for <test[*] ( )> )>
    >>> app.tick()
    >>> x
    <Value ('Hello World!') result=True; errors=False; for <test[*] ( )>
    >>> x.value
    'Hello World!'
    >>> 

The :py:attr:`Value.notify` attribute can also be
set to the name of an event which should be used
to fire the ``value_changed`` event to.

If the form ``x.notify = True`` used then the event that
gets fired is a concatenation of the original event
and the ``value_changed`` event. e.g: ``foo_value_changed``.

.. note:: This is a bit advanced and should only be used
          by experienced users of the circuits framework.
          If you simply want basic synchronization of
          event handlers it's recommended that you try
          the :meth:`circuits.Component.call`
          and :meth:`circuits.Component.wait`
          synchronization primitives first.
