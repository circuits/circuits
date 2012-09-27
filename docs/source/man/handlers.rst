Handlers
========

Explicit handler definition
---------------------------

Handlers are methods of components that are invoked when a matching
event is dispatched. The question arises how methods are made known
as handlers to the circuits framework.

The ability to define methods as handlers is already provided for in 
:class:`~circuits.core.components.Component`'s base class, the
:class:`~circuits.core.components.BaseComponent`. Any class that
inherits from ``BaseComponent`` can advertise a method as a handler
using the handler annotation.

.. literalinclude:: examples/handler_annotation.py
   :language: python
   :linenos:

:download:`Download handler_annotation.py <examples/handler_annotation.py>`

The handler annotation in line 14 makes the method ``_on_started`` known
to circuits as a handler for the event ``Started``. Event names used to define
handlers are the uncameled class names of the event. An event with a class 
name ``MySpecialEvent`` becomes "``my_special_event``" when referred to
in a handler definition. The name of the method that is annotated with
``@handler`` is of no significance. You can choose it to your liking.
Throughout the circuits source code, handler methods usually follow
the pattern "``_on_some_event``". This makes it obvious to the reader 
that the method is not part of the class's public API (leading underscore as
per Python convention) and that it is invoked for events of type
``SomeEvent``.

The optional keyword argument "``channel``" can be used to attach the
handler to a different channel than the component's channel (as specified
by the component's channel attribute).

Handler methods must be declared with arguments and keyword arguments that
match the arguments passed to the event upon its creation. Looking at the
API for :class:`~circuits.core.events.Started` you'll find that the
component that has been started is passed as an argument to its constructor.
Therefore, our handler method must declare one argument (line 15).

The handler annotation accepts some more keyword arguments that 
influence the behavior of the handler and its invocation. Details can
be found in the API description of :func:`~circuits.core.handlers.handler`.


Automatic handler definition
----------------------------

To easy the implementation of components with (mostly) standard
handlers, components can be derived from 
:class:`~circuits.core.components.Component`. For such classes a
``@handler("method_name")`` annotation is applied automatically 
to all method, unless the method's name starts with an underscore
or the method has already an explicit ``@handler`` annotation.  
