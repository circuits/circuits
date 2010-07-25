Features
========

Core Features:

* Event Driven (*message passing*)
* Component Architecture (*directed graph of components*)
* Event Feedback Channels (*callbacks*)
* Event Handler Inheritance (*component polymorphism*)
* Values and Future Values (*returned, deferred and future values*)
* Remote Bridging (*remote support*)
* Asynchronous Networking and I/O (*non-blocking*)

Networking (components):

* TCPServer, TCPClient
* UDPServer, UDPClient
* UNIXServer, UNIXClient
* Pipe

Polling (*components*):

* Select, Poll, EPoll

Protocol (*components*):

* Line, IRC, HTTP

Other Features:

* Small and lightweight.
* Pure python implementation. No C extension modules required.
* Compatible with Python 2.5, 2.6, 2.7 and 3.x (*coming soon*).
* High performance event framework (See:
  `Performance <http://bitbucket.org/prologic/circuits/wiki/Performance>`_
  on the wiki).
* Built-in developer tools: ``Debugger, circuits.tools``
* Application components: ``Daemon``, ``Log``.
* Asynchronous I/O components: ``File``, ``Serial``.
* Web framework: ``circuits.web``
