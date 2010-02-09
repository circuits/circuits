from circuits.web import Server, Controller

def pytest_funcarg__app(request):
    """ provide an initialized Server - it will lookup Root and Sessions
    from the module namespace where the 'app' funcarg is used and setup
    the server accordingly. The started 'app' server is shared across 
    each test module and will be teared down when the last test in the
    module was run. """
    return request.cached_setup(
        setup=lambda: setupapp(request),
        teardown=lambda app: teardownapp(app),
        scope="module")

def setupapp(request):
    Root = getattr(request.module, "Root")
    Sessions = getattr(request.module, "Sessions", None)
    if Sessions:
        app = Server(8000) + Sessions() + Root()
    else:
        app = Server(8000) + Root()
    app.hostport = app.host.split(":")
    app.start()
    print ("server started")
    return app

def teardownapp(app):
    print ("shutting down server")
    app.stop()
    
