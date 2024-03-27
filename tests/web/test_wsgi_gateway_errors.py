import pytest

from .helpers import HTTPError, urlopen


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    raise Exception('Hello World!')


def test(webapp):
    with pytest.raises(HTTPError) as exc:
        urlopen(webapp.server.http.base)
    assert exc.value.code == 500
    assert exc.value.msg == 'Internal Server Error'
    s = exc.value.read()
    assert b'Exception' in s
    assert b'Hello World!' in s
