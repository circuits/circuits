Manager
=======


.. module:: circuits.core.manager


The :mod:`~circuits.core` :class:`~Manager`
class is the base class of all components
in circuits. It is what defines the API(s)
of all components and necessary machinery
to run your application smoothly.

.. note:: It is not recommended to actually use
          the :class:`~Manager` in your application
          code unless you know what you're doing.

.. warning:: A :class:`~Manager` **does not** know
             how to register itself to other components!
             It is a manager, not a component, however
             it does form the basis of every component.


Usage
-----


Using the :class:`~Manager` in your application is
not really recommended except in some special
circumstances where you want to have a top-level
object that you can register things to.

Example:

.. code-block:: python
    :linenos:
    
    from circuits import Component, Manager
    
    
    class App(Component):
        """Your Application"""
    
    
    manager = Manager()
    App().register(manager)
    manager.run()


.. note:: If you *think* you need a :class:`~Manager`
          chances are you probably don't. Use a
          :class:`~circuits.core.components.Component`
          instead.
