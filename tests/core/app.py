from circuits import Component


class App(Component):

    def test(self):
        return "Hello World!"

    def prepare_unregister(self, *args):
        return
