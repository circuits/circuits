import pytest

from circuits.net.sockets import TCPServer

try:
    from socket import SOL_SOCKET, SO_REUSEPORT
except ImportError:
    pytestmark = pytest.mark.skip(reason='Missing SO_REUSEPORT')


def test_socket_options_server():
    s = TCPServer(('0.0.0.0', 8090), socket_options=[(SOL_SOCKET, SO_REUSEPORT, 1)])
    assert s._sock.getsockopt(SOL_SOCKET, SO_REUSEPORT) == 1
