"""VirtualHost

This module implements a virtual host dispatcher that sends requests
for configured virtual hosts to different dispatchers.
"""
from circuits import BaseComponent, handler
from circuits.six.moves.urllib_parse import urljoin


class VirtualHosts(BaseComponent):

    """Forward to anotehr Dispatcher based on the Host header.

    This can be useful when running multiple sites within one server.
    It allows several domains to point to different parts of a single
    website structure. For example:
    - http://www.domain.example      -> /
    - http://www.domain2.example     -> /domain2
    - http://www.domain2.example:443 -> /secure

    :param domains: a dict of {host header value: virtual prefix} pairs.
    :type  domains: dict

    The incoming "Host" request header is looked up in this dict,
    and, if a match is found, the corresponding "virtual prefix"
    value will be prepended to the URL path before passing the
    request onto the next dispatcher.

    Note that you often need separate entries for "example.com"
    and "www.example.com". In addition, "Host" headers may contain
    the port number.
    """

    channel = "web"

    def __init__(self, domains):
        super(VirtualHosts, self).__init__()

        self.domains = domains

    @handler("request", priority=1.0)
    def _on_request(self, event, request, response):
        path = request.path.strip("/")

        header = request.headers.get
        domain = header("X-Forwarded-Host", header("Host", ""))
        prefix = self.domains.get(domain, "")

        if prefix:
            path = urljoin("/%s/" % prefix, path)
            request.path = path
