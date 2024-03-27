"""stompest StompFrameTransport allowing for ssl.wrap_socket"""

import logging
import socket
import ssl


try:
    from stompest.error import StompConnectionError
    from stompest.sync.transport import StompFrameTransport
except ImportError:
    raise ImportError('No stomp support available. Is stompest installed?')

LOG = logging.getLogger(__name__)


class EnhancedStompFrameTransport(StompFrameTransport):
    """add support for older ssl module and http proxy"""

    proxy_host = None
    proxy_port = None
    proxy_user = None
    proxy_password = None

    def connect(self, timeout=None):
        """Allow older versions of ssl module, allow http proxy connections"""
        LOG.debug('stomp_transport.connect()')
        ssl_params = None
        if isinstance(self.sslContext, dict):
            # This is actually a dictionary of ssl parameters for wrapping the socket
            ssl_params = self.sslContext
            self.sslContext = ssl.create_default_context()
            if ssl_params['ca_certs']:
                self.sslContext.load_verify_locations(cafile=ssl_params['ca_certs'])
            self.sslContext.load_cert_chain(certfile=ssl_params['cert_file'], keyfile=ssl_params['key_file'])
            cert_required = ssl.CERT_REQUIRED if ssl_params['ca_certs'] else ssl.CERT_NONE
            self.sslContext.verify_mode = cert_required
            self.sslContext.minimum_version = ssl_params['ssl_version']

        try:
            if self.proxy_host:
                try:
                    # Don't try to import this unless we need it
                    import socks
                except ImportError:
                    raise ImportError('No http proxy support available. Is pysocks installed?')

                LOG.info('Connecting through proxy %s', self.proxy_host)
                self._socket = socks.socksocket()
                self._socket.set_proxy(
                    socks.HTTP, self.proxy_host, self.proxy_port, True, username=self.proxy_user, password=self.proxy_password
                )
            else:
                self._socket = socket.socket()

            self._socket.settimeout(timeout)
            self._socket.connect((self.host, self.port))

            if self.sslContext:
                self._socket = self.sslContext.wrap_socket(self._socket, server_hostname=self.host)

        except OSError as e:
            raise StompConnectionError('Could not establish connection [%s]' % e)
        self._parser.reset()
