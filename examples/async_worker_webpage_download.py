from time import sleep

import requests

from circuits import Component, Debugger, Event, Timer, Worker, task


def download_web_page(url):
    print('Downloading {}'.format(url))
    response = requests.get(url)
    sleep(2)  # This website is really slow.
    # Only returning portion of web page.
    # You would probably process web page for data before sending back
    return response.text[:200]


class App(Component):

    def init(self, *args, **kwargs):
        self.foo_count = 0
        Worker(process=False).register(self)

    def foo(self):
        self.foo_count += 1
        print("Foo!")
        if self.foo_count > 10:
            self.stop()

    def started(self, component):
        # x = yield self.call(task(factorial, 10))
        Timer(1, Event.create("foo"), persist=True).register(self)
        self.fire(task(download_web_page, 'http://www.slickdeals.net'))  # async
        self.fire(task(download_web_page, 'http://www.google.com'))  # async
        self.fire(task(download_web_page, 'http://www.yahoo.com'))  # async

    def task_success(self, function_called, function_result):
        func, url_called = function_called
        print('url {} gave {}'.format(url_called, function_result))


if __name__ == '__main__':
    app = App()
    Debugger().register(app)
    app.run()
