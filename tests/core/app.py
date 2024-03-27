from circuits import Component


class App(Component):
    def test(self) -> str:
        return 'Hello World!'

    def prepare_unregister(self, *args) -> None:
        return
