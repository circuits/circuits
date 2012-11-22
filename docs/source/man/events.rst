Events
======

Basic usage
-----------

Events are objects that are fired by the circuits framework implicitly
(like the :class:`~circuits.core.events.Started` event used in the tutorial) 
or explicitly by components while handling some other event. Once fired,
events are dispatched to the components that are interested in these events,
i.e. that have registered themselves as handlers for these events.

Events are usually fired on one or more channels, allowing components 
to gather in "interest groups". This is especially useful if you want to
reuse basic components such as a TCP server. A TCP server component
fires a ``Read`` event for every package of data that it receives. If we 
hadn't the channels, it would be very difficult to separate the data from 
two different TCP connections. But using the channels, we can put one TCP 
server and all components interested in its events on one channel, and 
another TCP server and the components interested in this other TCP server's 
events on another channel. Components are associated with a channel by
setting their ``channel`` attribute (see API description for 
:class:`~.components.Component`).

Besides having a name, events carry additional arbitrary information.
This information is passed as arguments or keyword arguments to the
constructor. It is then delivered to the handler function that must have
exactly the same number of arguments and keyword arguments. Of course,
as is usual in Python, you can also pass additional information by setting
attributes of the event object, though this usage pattern is discouraged
for events.

Events as result collectors
---------------------------

Apart from delivering information to handlers, event objects may also collect 
information. If a handler returns something that is not ``None``, it is
stored in the event's ``value`` attribute. If a second (or any subsequent)
handler invocation also returns a value, the values are stored as a list.
Note that the value attribute is of type :class:`~.values.Value` and you
must access its property ``value`` to access the data stored 
(``collected_information = event.value.value``).

The collected information can be accessed by handlers in order to find out
about any return values from the previously invoked handlers. More useful
though, is the possibility to access the information after all handlers
have been invoked. After all handlers have run successfully (i.e. no
handler has thrown an error) circuits may generate an event that indicates
the successful handling. This event has the name of the event
just handled with "Success" appended. So if the event is called ``Identify``
then the success event is called ``IdentifySuccess``. Success events aren't
delivered by default. If you want successful handling to be indicated 
for an event, you have to set the optional attribute ``success`` of this 
event to ``True``.

The handler for a success event must be defined with two arguments. When
invoked, the first argument is the event just having been handled 
successfully and the second argument is (as a convenience) what has been
collected in ``event.value.value`` (note that the first argument may not
be called ``event``, for an explanation of this restriction as well as
for an explanation why the method is called ``identify_success`` 
see the section on handlers). 

.. literalinclude:: examples/handler_returns.py
   :language: python
   :linenos:

:download:`Download handler_returns.py <examples/handler_returns.py>`


Advanced usage
--------------

Sometimes it may be necessary to take some action when all state changes
triggered by an event are in effect. In this case it is not sufficient
to wait for the completion of all handlers for this particular event. 
Rather, we also have to wait until all events that have been fired by 
those handlers have been processed (and again wait for the events fired by
those events' handlers, and so on). To support this scenario, circuits 
can fire a ``Complete`` event. The usage is similar to the previously 
described success event. Details can be found in the API description of
:class:`circuits.core.events.Event`.


