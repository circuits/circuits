from circuits.net.sockets import BUFSIZE
from circuits.web.servers import BaseServer


class MockClass(BaseServer):
    pass


def test_dynamic_bufsize_in_baseserver():
    bufsize = 10000
    try:
        # Assert when we set BUFSIZE ourselves
        mock = MockClass(bind="0.0.0.0:1234", bufsize=bufsize)
        # that it will be set to our given value
        assert bufsize == mock.server._bufsize
    finally:
        mock.server.unregister()
        mock.stop()


def test_constant_bufsize_in_baseserver():
    try:
        # Assert when we dont set BUFSIZE ourself
        mock = MockClass(bind="0.0.0.0:1235")
        # that it will be set to the constant default value
        assert mock.server._bufsize == BUFSIZE
    finally:
        mock.server.unregister()
        mock.stop()
