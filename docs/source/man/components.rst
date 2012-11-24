Components
==========

The architectural concept of circuits is to encapsulate system 
functionality into discrete manageable and reusable units, called *Components*, 
that interact by sending and handling events that flow throughout the system.

Technically, a circuits *Component* is a Python class that inherits
(directly or indirectly) from 
:class:`~circuits.core.components.BaseComponent`.

Components can be sub-classed like any other normal Python class, however
components can also be composed of other components and it is natural
to do so. These are called *Complex Components*. An example of a Complex
Component within the circuits library is the 
:class:`circuits.web.servers.Server` Component which is comprised of:

- :class:`circuits.net.sockets.TCPServer`
- :class:`circuits.web.servers.BaseServer`
- :class:`circuits.web.http.HTTP`
- :class:`circuits.web.dispatchers.dispatcher.Dispatcher`

Note that there is no class or other technical means to mark a component
as a complex component. Rather, all component instances in a circuits 
based application belong to some component tree (there may be several),
with Complex Components being a subtree within that structure.

A Component is attached to the tree by registering with the parent and
detached by un-registering itself (methods
:meth:`~circuits.core.components.BaseComponent.register` and
:meth:`~circuits.core.components.BaseComponent.unregister` of 
``BaseComponent``).