.. _#circuits IRC Channel: http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4
.. _Mailing List: http://groups.google.com/group/circuits-users

.. faq:

Frequently Asked Questions
==========================


.. general:

General
-------

...  What is circuits?
   circuits is an event-driven framework with a high focus on Component
   architectures making your life as a software developer much easier.
   circuits allows you to write maintainable and scalable systems easily

... Can I write networking applications with circuits?
   Yes absolutely. circuits comes with socket I/O components for tcp, udp
   and unix sockets with asynchronous polling implementations for select,
   poll, epoll and kqueue.

... Can I integrate circuits with a GUI library?
   This is entirely possible. You will have to hook into the GUI's main loop.

... What are the core concepts in circuits?
   Components and Events. Components are maintainable reusable units of
   behavior that communicate with other components via a powerful message
   passing system.

... How would you compare circuits to Twisted?
   Others have said that circuits is very elegant in terms of it's usage.
   circuits' component architecture allows you to define clear interfaces
   between components while maintaining a high level of scalability and
   maintainability.

... Can Components communicate with other processes?
   Yes. circuits implements currently component bridging and nodes

... What platforms does circuits support?
   circuits currently supports Linux, FreeBSD, OSX and Windows and is
   currently continually tested against Linux and Windows against Python
   versions 2.7, 3.4, 3.5 and 3.6

... Can circuits be used for concurrent or distributed programming?
   Yes. We also have plans to build more distributed components into circuits
   making distributing computing with circuits very trivial.

Got more questions?

* Send an email to our `Mailing List`_.
* Talk to us online on the `#circuits IRC Channel`_
