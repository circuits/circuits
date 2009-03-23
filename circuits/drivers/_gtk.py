# Module:   pygame_driver
# Date:     14th March 2009
# Author:   Ali Afshar aafshar at gmail dot com

"""GTK Driver

Driver to integrate with gtk
"""

from circuits import Component
from circuits.tools import graph, inspect


try:
    import gtk
    gtk.gdk.threads_init()
except ImportError:
    raise Exception("No gtk support available. Is gtk installed?")


class GtkDriver(Component):

    channel = "gtk"

    def __tick__(self):
        while gtk.events_pending():
            gtk.main_iteration_do(block=False)


def test():
    import gobject
    from circuits import Manager, Debugger
    from circuits.web import BaseServer, wsgi



    w = gtk.Window()
    vb = gtk.VBox()
    tv = gtk.TextView()
    sw = gtk.ScrolledWindow()
    sw.add(tv)
    vb.pack_start(sw)
    w.add(vb)
    w.show_all()


    def dummy_app(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        def _write(data):
            b = tv.get_buffer()
            b.insert(b.get_end_iter(), data + '\n')
        gobject.idle_add(_write, '%(PATH_INFO)s %(REMOTE_ADDR)s %(SERVER_PROTOCOL)s' % environ)
        return ['hello world']

    class App(Manager):
        def __init__(self):
            Manager.__init__(self)

            self += GtkDriver()
            self += Debugger()

            self.server = BaseServer(9999)

            self.server += wsgi.Gateway(dummy_app)

            self += self.server

    app = App()
    def on_delete(window, event):
        app.stop()
    w.connect('delete-event', on_delete)
    w.resize(200, 200)
    app.run()

def test2():
    import gobject
    from circuits import Manager, Debugger
    from circuits.net.sockets import TCPClient, Connect, Write

    m = Manager()
    m += GtkDriver()
    m += Debugger()

    def on_delete(window, event):
        m.stop()

    w = gtk.Window()
    w.connect('delete-event', on_delete)
    vb = gtk.VBox()

    b = gtk.Button('Click me')

    tv = gtk.TextView()
    sw = gtk.ScrolledWindow()
    sw.add(tv)

    vb.pack_start(sw)

    class Wget(TCPClient):

        channel = "wget"

        def __init__(self, tv, host='google.com', port=80):
            super(Wget, self).__init__()

            self.tv = tv
            self += TCPClient(channel=self.channel)

        def fetch_google(self, *args):
            self.push(Connect('google.com', 80), "connect")

        def connected(self, host, port):
            print "Connected to %s" % host
            self.push(Write('GET / HTTP/1.0\r\n\r\n'))

        def error(self, *args):
            print "ERROR: %r" % list(args)

        def read(self, data):
            def _write(data):
                self.tv.get_buffer().set_text(data)
            gobject.idle_add(_write, data)

    wg = Wget(tv)
    m += wg

    def on_click(self, wget):
        tv.get_buffer().set_text('')
        wget.fetch_google()


    b.connect('clicked', on_click, wg)
    vb.pack_start(b, expand=False)
    w.add(vb)
    w.show_all()

    print graph(m)
    print inspect(m)

    m.run()



if __name__ == '__main__':
    test()
