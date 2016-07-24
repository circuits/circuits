Debugger
========


.. module:: circuits.core.debugger


The :mod:`~circuits.core` :class:`~Debugger`
component is the standard way to debug your
circuits applications. It services two purposes:

- Logging events as they flow through the system.
- Logging any exceptions that might occurs in your application.


Usage
-----


Using the :class:`~Debugger` in your application is
very straight forward just like any other component
in the circuits component library. Simply add it
to your application and register it somewhere
(*it doesn't matter where*).


Example:

.. code-block:: python
    :linenos:
    
    from circuits import Component, Debugger
    
    
    class App(Component):
        """Your Application"""
    
    
    app = App()
    Debugger().register(app)
    app.run()


Sample Output(s)
----------------


Here are some example outputs that you should
expect to see when using the :class:`~Debugger`
component in your application.

Example Code:

.. code-block:: python
    :linenos:
       
    from circuits import Event, Component, Debugger
    
    
    class foo(Event):
        """foo Event"""
    
    
    class App(Component):
    
        def foo(self, x, y):
            return x + y
    
    
    app = App() + Debugger()
    app.start()

Run with::
    
    python -i app.py

Logged Events::
    
    <registered[*] (<Debugger/* 27098:App (queued=0) [S]>, <App/* 27098:App (queued=2) [R]> )>
    <started[*] (<App/* 27098:App (queued=1) [R]> )>
    >>> app.fire(foo(1, 2))
    <Value () result=False; errors=False; for <foo[*] (1, 2 )>
    >>> <foo[*] (1, 2 )>

Logged Exceptions::
    
    >>> app.fire(foo())
    <Value () result=False; errors=False; for <foo[*] ( )>
    >>> <foo[*] ( )>
    <exception[*] (<type 'exceptions.TypeError'>, TypeError('foo() takes exactly 3 arguments (1 given)',), ['  File "/home/prologic/work/circuits/circuits/core/manager.py", line 561, in _dispatcher\n    value = handler(*eargs, **ekwargs)\n'] handler=<bound method App.foo of <App/* 27098:App (queued=1) [R]>>, fevent=<foo[*] ( )>)>
    ERROR <handler[*][foo] (App.foo)> (<foo[*] ( )>) {<type 'exceptions.TypeError'>}: foo() takes exactly 3 arguments (1 given)
      File "/home/prologic/work/circuits/circuits/core/manager.py", line 561, in _dispatcher
          value = handler(*eargs, **ekwargs)
