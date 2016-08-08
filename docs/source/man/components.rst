.. module:: circuits.core.components


Components
==========


The architectural concept of circuits is to encapsulate system 
functionality into discrete manageable and reusable units, called *Components*, 
that interact by sending and handling events that flow throughout the system.

Technically, a circuits *Component* is a Python class that inherits
(*directly or indirectly*) from 
:class:`~BaseComponent`.

Components can be sub-classed like any other normal Python class, however
components can also be composed of other components and it is natural
to do so. These are called *Complex Components*. An example of a Complex
Component within the circuits library is the 
:class:`circuits.web.servers.Server` Component which is comprised of:

- :class:`circuits.net.sockets.TCPServer`
- :class:`circuits.web.servers.BaseServer`
- :class:`circuits.web.http.HTTP`
- :class:`circuits.web.dispatchers.dispatcher.Dispatcher`

.. note:: There is no class or other technical means to mark a component
          as a complex component. Rather, all component instances in a circuits 
          based application belong to some component tree (there may be several),
          with Complex Components being a subtree within that structure.

A Component is attached to the tree by registering with the parent and
detached by unregistering itself. See methods:

- :meth:`~BaseComponent.register`
- :meth:`~BaseComponent.unregister`

The hierarchy of components facilitates addition and removal of complex components at runtime. 

All registered components in the hierarchy receive all applicable events regardless of lineage.  

Component Registration
----------------------


To register a component use the :meth:`~Component.register` method.

.. code-block:: python
    :linenos:
    
    from circuits import Component


    class Foo(Component):
        """Foo Component"""


    class  App(Component):
        """App Component"""

        def init(self):
            Foo().register(self)


    app = App()
    debugger = Debugger().register(app)
    app.run()


Unregistering Components
------------------------


Components are unregistered via the :meth:`~Component.unregister` method.

.. code-block:: python
    
   debugger.unregister()

.. note:: You need a reference to the component you wish to
          unregister. The :meth:`~Component.register` method
          returns you a reference of the component that was
          registered.


Convenient Shorthand Form
-------------------------


After a while when your application becomes rather large
and complex with many components and component registrations
you will find it cumbersome to type ``.register(blah)``.

circuits has several convenient methods for component
registration and deregistration that work in an identical
fashion to their :meth:`~Component.register` and
:meth:`~Component.unregister` counterparts.

These convenience methods follow normal mathematical
operator precedence rules and are implemented by
overloading the Python ``__add__``, ``__iadd__``,
``__sub__`` and ``__isub__``.

The mapping is as follow:

- :meth:`~Component.register` map to ``+`` and ``+=``
- :meth:`~Component.unregister` map to> ``-`` and ``-=``

For example the above could have been written as:

.. code-block:: python
    :linenos:
    
    from circuits import Component


    class Foo(Component):
        """Foo Component"""


    class  App(Component):
        """App Component"""

        def init(self):
            self += Foo()


    (App() + Debugger()).run()


Implicit Component Registration(s)
----------------------------------


Sometimes it's handy to implicitly register
components into another component by simply
referencing the other component instance as
a class attribute of the other.

Example:

.. code-block:: python
    
    >>> from circuits import Component
    >>> 
    >>> class Foo(Component):
    ...     """Foo Component"""
    ... 
    >>> class App(Component):
    ...     """App Component"""
    ...     
    ...     foo = Foo()
    ... 
    >>> app = App()
    >>> app.components
    set([<Foo/* 28599:MainThread (queued=0) [S]>])
    >>> 

The `telnet Example <https://github.com/circuits/circuits/tree/master/examples/telnet.py>`_
does this for example.
