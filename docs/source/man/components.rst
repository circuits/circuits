Components
==========

In circuits, a ``Component`` is a special class designed to allow one to
encapsulate system functionality into discrete manageable units.

Components are **registered** together to form a complete system of interacting
components that listen and react to events that flow throughout the system.

Components can be sub-classed like any other normal Python class, however
components can also be **composed** of other components and it is natural
to do so. These are called **Complex Components**. An example of a Complex
Component within the circuits library is the ``circuits.web.servers.Server``
Component which is comprised of:

- ``circuits.net.sockets.TCpServer``
- ``circuits.web.servers.BaseServer``
- ``circuits.web.http.HTTP``
- ``circuits.web.dispatchers.dispatcher.Dispatcher``

