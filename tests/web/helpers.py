from http.cookiejar import CookieJar  # noqa
from urllib.error import HTTPError, URLError  # noqa
from urllib.parse import (  # noqa
    quote, urlencode, urljoin, urlparse,
)
from urllib.request import (  # noqa
    HTTPBasicAuthHandler, HTTPCookieProcessor, HTTPDigestAuthHandler, Request,
    build_opener, install_opener, urlopen,
)

# pylama:skip=1
