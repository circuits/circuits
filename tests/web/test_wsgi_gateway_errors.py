from .helpers import HTTPError, urlopen


def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    raise Exception("Hello World!")


def test(webapp):
    try:
        urlopen(webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 500
        assert e.msg == "Internal Server Error"
        s = e.read()
        assert b"Exception" in s
        assert b"Hello World!" in s
    else:
        assert False
