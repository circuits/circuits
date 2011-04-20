from circuits.web import Controller

class Test(Controller):

    channel = "/test"

    def index(self):
        return "This is /test!"
