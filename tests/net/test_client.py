#!/usr/bin/env python
from socket import gaierror


def test_client_bind_int():
    from circuits.net.sockets import Client

    class TestClient(Client):

        def _create_socket(self):
            return None

    client = TestClient(1234)

    assert client._bind[1] == 1234


def test_client_bind_int_gaierror(monkeypatch):
    from circuits.net import sockets

    def broken_gethostname():
        raise gaierror()

    monkeypatch.setattr(sockets, "gethostname", broken_gethostname)

    class TestClient(sockets.Client):

        def _create_socket(self):
            return None

    client = TestClient(1234)

    assert client._bind == ("0.0.0.0", 1234)


def test_client_bind_str():
    from circuits.net.sockets import Client

    class TestClient(Client):

        def _create_socket(self):
            return None

    client = TestClient("0.0.0.0:1234")

    assert client._bind == ("0.0.0.0", 1234)
