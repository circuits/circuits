Hello
.....


.. code:: python
    
    #!/usr/bin/env python
    
    """circuits Hello World"""
    
    from circuits import Component, Event
    
    
    class hello(Event):
        """hello Event"""
    
    
    class App(Component):
    
        def hello(self):
            """Hello Event Handler"""
            
            print("Hello World!")
        
        def started(self, component):
            """Started Event Handler
            
            This is fired internally when your application starts up and can be used to
            trigger events that only occur once during startup.
            """
            
            self.fire(hello())  # Fire hello Event
            
            raise SystemExit(0)  # Terminate the Application
    
    App().run()


Echo Server
...........


.. code:: python
    
    #!/usr/bin/env python
    
    """Simple TCP Echo Server
    
    This example shows how you can create a simple TCP Server (an Echo Service)
    utilizing the builtin Socket Components that the circuits library ships with.
    """
    
    from circuits import handler, Debugger
    from circuits.net.sockets import TCPServer
    
    
    class EchoServer(TCPServer):
        
        @handler("read")
        def on_read(self, sock, data):
            """Read Event Handler
            
            This is fired by the underlying Socket Component when there has been
            new data read from the connected client.
            
            ..note :: By simply returning, client/server socket components listen
                      to ValueChagned events (feedback) to determine if a handler
                      returned some data and fires a subsequent Write event with
                      the value returned.
            """
            
            return data
    
    # Start and "run" the system.
    # Bind to port 0.0.0.0:9000
    app = EchoServer(9000)
    Debugger().register(app)
    app.run()


Hello Web
.........


.. code:: python
    
    #!/usr/bin/env python
    
    from circuits.web import Server, Controller
    
    
    class Root(Controller):
        
        def index(self):
            """Index Request Handler
            
            Controller(s) expose implicitly methods as request handlers.
            Request Handlers can still be customized by using the ``@expose``
            decorator. For example exposing as a different path.
            """
            
            return "Hello World!"
    
    app = Server(("0.0.0.0", 9000))
    Root().register(app)
    app.run()


More `examples <https://github.com/circuits/circuits/tree/master/examples>`_...
