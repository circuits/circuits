try:
    from urllib.error import HTTPError, URLError
    from urllib.parse import quote, urlencode, urljoin
    from urllib.request import HTTPBasicAuthHandler, HTTPCookieProcessor
    from urllib.request import urlopen, build_opener, install_opener
    from urllib.request import HTTPDigestAuthHandler, Request
except ImportError:
    from urlparse import urljoin
    from urllib import quote, urlencode
    from urllib2 import HTTPError, URLError, HTTPDigestAuthHandler
    from urllib2 import HTTPBasicAuthHandler, HTTPCookieProcessor
    from urllib2 import urlopen, build_opener, install_opener, Request

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

# pylama:skip=1
