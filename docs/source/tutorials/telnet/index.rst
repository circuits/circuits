.. _Python Programming Language: http://www.python.org/


Telnet Tutorial
===============


Overview
--------

Welcome to our 2nd circuits tutorial. This tutorial is going to walk you
through the `telnet Example <https://github.com/circuits/circuits/tree/master/examples/telnet.py>`_
showing you how to various parts of the circuits component library for
building a simple TCP client that also accepts user input.

Be sure you have circuits installed before you start:

.. code-block:: bash
    
    pip install circuits


See: :doc:`../../start/installing`


Components
----------

You will need the following components:

1. The :class:`~.net.sockets.TCPClient` Component
2. The :class:`~.io.file.File` Component
3. The :class:`~.Component` Component

All these are available in the circuits library
so there is nothing for you to do.
Click on each to read more about them.


Design
------

.. graphviz:: Telnet.dot

The above graph is the overall design of our Telnet
application. What's shown here is a relationship
of how the components fit together and the overall
flow of events.

For example:

1. Connect to remote TCP Server.
2. Read input from User.
3. Write input from User to connected Socket.
4. Wait for data from connected Socket and display.

.. note:: The :class:`~.core.pollers.Select` Component shown
          is required by our application for Asynchronous I/O
          polling however we do not need to explicitly use it
          as it is automatically imported and registered simply
          by utilizing the :class:`~.net.sockets.TCPClient` Component.


Implementation
--------------

Without further delay here's the code:

.. literalinclude:: telnet.py
   :language: python
   :linenos:

:download:`Download telnet.py <telnet.py>`


Discussion
----------

Some important things to note...

1. Notice that we defined a ``channel`` for out ``Telnet`` Component?

   This is so that the events of :class:`~.net.sockets.TCPClient` and
   :class:`~.io.file.File` don't collide. Both of these components
   share a very similar interface in terms of the events they listen to.

.. code-block:: python
    
    class Telnet(Component):

        channel = "telnet"

2. Notice as well that in defining a ``channel`` for our ``Telnet``
   Component we've also "registered" the :class:`~.net.sockets.TCPClient`
   Component so that it has the same channel as our ``Telnet`` Component.

   Why? We want our ``Telnet`` Component to receive all of the events of
   the :class:`~.net.sockets.TCPClient` Component.

.. code-block:: python
    
    TCPClient(channel=self.channel).register(self)

3. In addition to our :class:`~.net.sockets.TCPClient` Component being
   registered with the same ``channel`` as our ``Telnet`` Component
   we can also see that we have registered a :class:`~.io.file.File`
   Component however we have chosen a different channel here called ``stdin``.

   Why? We don't want the events from :class:`~.net.sockets.TCPClient` and subsequently
   our ``Telnet`` Component to collide with the events from :class:`~.io.file.File`.

   So we setup a Component for reading user input by using the :class:`~.io.file.File`
   Component and attaching an event handler to our ``Telnet`` Component but listening
   to events from our ``stdin`` channel.

.. code-block:: python
    
    File(sys.stdin, channel="stdin").register(self)

.. code-block:: python
    
    @handler("read", channel="stdin")
    def read_user_input(self, data):
        self.fire(write(data))

Here is what the event flow would look like if
you were to register the :class:`~.Debugger`
to the ``Telnet`` Component.

.. code-block:: python
    
    from circuits import Debugger
    (Telnet(host, port) + Debugger()).run()

.. code-block:: bash
    
    $ python telnet.py 10.0.0.2 9000
    <registered[telnet] (<TCPClient/telnet 21995:MainThread (queued=0) [S]>, <Telnet/telnet 21995:MainThread (queued=4) [R]> )>
    <registered[stdin] (<File/stdin 21995:MainThread (queued=0) [S]>, <Telnet/telnet 21995:MainThread (queued=5) [R]> )>
    <registered[*] (<Debugger/* 21995:MainThread (queued=0) [S]>, <Telnet/telnet 21995:MainThread (queued=5) [R]> )>
    <started[telnet] (<Telnet/telnet 21995:MainThread (queued=4) [R]> )>
    <registered[select] (<Select/select 21995:MainThread (queued=0) [S]>, <TCPClient/telnet 21995:MainThread (queued=0) [S]> )>
    <ready[telnet] (<TCPClient/telnet 21995:MainThread (queued=0) [S]> )>
    <ready[stdin] (<File/stdin 21995:MainThread (queued=0) [S]> )>
    <connect[telnet] ('10.0.0.2', 9000 )>
    <_open[stdin] ( )>
    <connected[telnet] ('10.0.0.2', 9000 )>
    <opened[stdin] ('<stdin>', 'r' )>
    Hello World!
    <_read[stdin] (<open file '<stdin>', mode 'r' at 0x7f32ff5ab0c0> )>
    <read[stdin] ('Hello World!\n' )>
    <write[telnet] ('Hello World!\n' )>
    <_write[telnet] (<socket._socketobject object at 0x11f7f30> )>
    <_read[telnet] (<socket._socketobject object at 0x11f7f30> )>
    <read[telnet] ('Hello World!\n' )>
    Hello World!
    ^C<signal[telnet] (2, <frame object at 0x12b0a10> )>
    <stopped[telnet] (<Telnet/telnet 21995:MainThread (queued=0) [S]> )>
    <close[telnet] ( )>
    <close[stdin] ( )>
    <disconnected[telnet] ( )>
    <closed[stdin] ( )>


Testing
-------

To try this example out, download a copy of the
`echoserver Example <https://github.com/circuits/circuits/tree/master/echoserver.py>`_
and copy and paste the full source code of the
``Telnet`` example above into a file called ``telnet.py``.

In one terminal run::
    
    $ python echoserver.py

In a second terminal run::
    
    $ python telnet.py localhost 9000

Have fun!

For more examples see `examples <https://github.com/circuits/circuits/tree/master/examples>`_.

.. seealso::
    - :doc:`../../faq`
    - :doc:`../../api/index`
