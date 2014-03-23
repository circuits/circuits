Events
======


Basic usage
-----------

Events are objects that contain data (*arguments and keyword arguments*) 
about the message being sent to a receiving component. Events are triggered
by using the :meth:`~circuits.core.manager.Manager.fire` method of any
registered component.

Some events in circuits are fired implicitly by the circuits core
like the :class:`~circuits.core.events.started` event used in the tutorial
or explicitly by components while handling some other event. Once fired,
events are dispatched to the components that are interested in these events
(*components whose event handlers match events of interest*).

Events are usually fired on one or more channels, allowing components 
to gather in "interest groups". This is especially useful if you want to
reuse basic components such as a :class:`~circuits.net.sockets.TCPServer`.
A :class:`~circuits.net.sockets.TCPServer` component fires a
:class:`~circuits.net.events.read` event for every package of data that it receives.
If we did not have support for channels, it would be very difficult to build two
servers in a single process without their read events colliding.

Using channels, we can put one server and all components interested in its events on one channel,
and another server and the components interested in this other server's events on another channel.

Components are associated with a channel by setting their ``channel`` class or instance attribute.

.. seealso:: :class:`~.components.Component`

Besides having a name, events carry additional arbitrary information.
This information is passed as arguments or keyword arguments to the
constructor. It is then delivered to the event handler method that must have
exactly the same number of arguments and keyword arguments. Of course,
as is usual in Python, you can also pass additional information by setting
attributes of the event object, though this usage pattern is discouraged.


Filtering
---------

Events can be filtered by stopping other event handlers from continuing to process the event.

To do this, simply call the :meth:`~circuits.core.events.Event.stop` method.

Example:

.. code-block:: python
    
    @handler("foo")
    def stop_foo(self, event, *args, **kwargs):
        event.stop()
    
Here any other event handlers also listening to "foo" will not be processed.

.. note:: It's important to use priority event handlers here in this case as all event handlers and events run with the same priority unless explicitly
          told otherwise.

.. versionchanged:: 3.0
   In circuits 2.x you declared your event handler to be a filter by using ``@handler(filter=True)`` and
   returned a ``True``-ish value from the respective event handler to achieve the same effect.
   This is **no longer** the case in circuits 3.x Please use ``event.stop()`` as noted above.


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


