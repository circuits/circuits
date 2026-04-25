"""
VirtualHost

This module implements a virtual host dispatcher that sends requests
for configured virtual hosts to different dispatchers.
"""

from urllib.parse import urljoin

from circuits import BaseComponent, handler


class VirtualHosts(BaseComponent):
    """
    Forward to anotehr Dispatcher based on the Host header.

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

    channel = 'web'

    def __init__(self, domains, trusted_proxies=None):
        super().__init__()

        self.domains = domains
        self.trusted_proxies = set(trusted_proxies or ())

    @handler('request', priority=1.0)
    def _on_request(self, event, request, response):
        path = request.path.strip('/')

        header = request.headers.get
        domain = header('Host', '').strip()

        if self.trusted_proxies:
            remote = getattr(request, 'remote', None)
            remote_ip = getattr(remote, 'ip', None)
            if remote_ip is None and isinstance(remote, (list, tuple)) and remote:
                remote_ip = remote[0]

            if remote_ip in self.trusted_proxies:
                forwarded = header('X-Forwarded-Host', '')
                if forwarded:
                    domain = forwarded.split(',', 1)[0].strip()

        prefix = self.domains.get(domain, '')

        if prefix:
            path = urljoin('/%s/' % prefix, path)
            request.path = path
