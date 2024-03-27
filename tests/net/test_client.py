#!/usr/bin/env python
from socket import gaierror
from typing import NoReturn


def test_client_bind_int() -> None:
    from circuits.net.sockets import Client

    class TestClient(Client):
        def _create_socket(self) -> None:
            return None

    client = TestClient(1234)

    assert client._bind[1] == 1234


def test_client_bind_int_gaierror(monkeypatch) -> None:
    from circuits.net import sockets

    def broken_gethostname() -> NoReturn:
        raise gaierror()

    monkeypatch.setattr(sockets, 'gethostname', broken_gethostname)

    class TestClient(sockets.Client):
        def _create_socket(self) -> None:
            return None

    client = TestClient(1234)

    assert client._bind == ('0.0.0.0', 1234)


def test_client_bind_str() -> None:
    from circuits.net.sockets import Client

    class TestClient(Client):
        def _create_socket(self) -> None:
            return None

    client = TestClient('0.0.0.0:1234')

    assert client._bind == ('0.0.0.0', 1234)
