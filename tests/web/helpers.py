try:
    from urllib.parse import urlencode
    from urllib.error import HTTPError, URLError
    from urllib.request import HTTPBasicAuthHandler, HTTPCookieProcessor
    from urllib.request import urlopen, build_opener, install_opener
    from urllib.request import HTTPDigestAuthHandler, Request
except ImportError:
    from urllib import urlencode
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
