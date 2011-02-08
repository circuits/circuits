import collections
import select
import string
import struct
try:
    from hashlib import md5
except ImportError: #pragma NO COVER
    from md5 import md5
from errno import EINTR
from socket import error as SocketError


class MalformedWebSocket(ValueError):
    pass


def _extract_number(value):
    """
    Utility function which, given a string like 'g98sd  5[]221@1', will
    return 9852211. Used to parse the Sec-WebSocket-Key headers.
    """
    out = ""
    spaces = 0
    for char in value:
        if char in string.digits:
            out += char
        elif char == " ":
            spaces += 1
    return int(out) / spaces


def setup_websocket(request):
    if request.META.get('HTTP_CONNECTION', None) == 'Upgrade' and \
        request.META.get('HTTP_UPGRADE', None) == 'WebSocket':

        # See if they sent the new-format headers
        if 'HTTP_SEC_WEBSOCKET_KEY1' in request.META:
            protocol_version = 76
            if 'HTTP_SEC_WEBSOCKET_KEY2' not in request.META:
                raise MalformedWebSocket()
        else:
            protocol_version = 75

        # If it's new-version, we need to work out our challenge response
        if protocol_version == 76:
            key1 = _extract_number(request.META['HTTP_SEC_WEBSOCKET_KEY1'])
            key2 = _extract_number(request.META['HTTP_SEC_WEBSOCKET_KEY2'])
            # There's no content-length header in the request, but it has 8
            # bytes of data.
            key3 = request.META['wsgi.input'].read(8)
            key = struct.pack(">II", key1, key2) + key3
            handshake_response = md5(key).digest()

        location = 'ws://%s%s' % (request.get_host(), request.path)
        qs = request.META.get('QUERY_STRING')
        if qs:
            location += '?' + qs
        if protocol_version == 75:
            handshake_reply = (
                "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
                "Upgrade: WebSocket\r\n"
                "Connection: Upgrade\r\n"
                "WebSocket-Origin: %s\r\n"
                "WebSocket-Location: %s\r\n\r\n" % (
                    request.META.get('HTTP_ORIGIN'),
                    location))
        elif protocol_version == 76:
            handshake_reply = (
                "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
                "Upgrade: WebSocket\r\n"
                "Connection: Upgrade\r\n"
                "Sec-WebSocket-Origin: %s\r\n"
                "Sec-WebSocket-Protocol: %s\r\n"
                "Sec-WebSocket-Location: %s\r\n" % (
                    request.META.get('HTTP_ORIGIN'),
                    request.META.get('HTTP_SEC_WEBSOCKET_PROTOCOL', 'default'),
                    location))
            handshake_reply = str(handshake_reply)
            handshake_reply = '%s\r\n%s' % (handshake_reply, handshake_response)

        else:
            raise MalformedWebSocket("Unknown WebSocket protocol version.")
        socket = request.META['wsgi.input']._sock.dup()
        return WebSocket(
            socket,
            protocol=request.META.get('HTTP_WEBSOCKET_PROTOCOL'),
            version=protocol_version,
            handshake_reply=handshake_reply,
        )
    return None


class WebSocket(object):
    """
    A websocket object that handles the details of
    serialization/deserialization to the socket.

    The primary way to interact with a :class:`WebSocket` object is to
    call :meth:`send` and :meth:`wait` in order to pass messages back
    and forth with the browser.
    """
    _socket_recv_bytes = 4096


    def __init__(self, socket, protocol, version=76,
        handshake_reply=None, handshake_sent=None):
        '''
        Arguments:

        - ``socket``: An open socket that should be used for WebSocket
          communciation.
        - ``protocol``: not used yet.
        - ``version``: The WebSocket spec version to follow (default is 76)
        - ``handshake_reply``: Handshake message that should be sent to the
          client when ``send_handshake()`` is called.
        - ``handshake_sent``: Whether the handshake is already sent or not.
          Set to ``False`` to prevent ``send_handshake()`` to do anything.
        '''
        self.socket = socket
        self.protocol = protocol
        self.version = version
        self.closed = False
        self.handshake_reply = handshake_reply
        if handshake_sent is None:
            self._handshake_sent = not bool(handshake_reply)
        else:
            self._handshake_sent = handshake_sent
        self._buffer = ""
        self._message_queue = collections.deque()

    def send_handshake(self):
        self.socket.sendall(self.handshake_reply)
        self._handshake_sent = True

    @classmethod
    def _pack_message(cls, message):
        """Pack the message inside ``00`` and ``FF``

        As per the dataframing section (5.3) for the websocket spec
        """
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        elif not isinstance(message, str):
            message = str(message)
        packed = "\x00%s\xFF" % message
        return packed

    def _parse_message_queue(self):
        """ Parses for messages in the buffer *buf*.  It is assumed that
        the buffer contains the start character for a message, but that it
        may contain only part of the rest of the message.

        Returns an array of messages, and the buffer remainder that
        didn't contain any full messages."""
        msgs = []
        end_idx = 0
        buf = self._buffer
        while buf:
            frame_type = ord(buf[0])
            if frame_type == 0:
                # Normal message.
                end_idx = buf.find("\xFF")
                if end_idx == -1: #pragma NO COVER
                    break
                msgs.append(buf[1:end_idx].decode('utf-8', 'replace'))
                buf = buf[end_idx+1:]
            elif frame_type == 255:
                # Closing handshake.
                assert ord(buf[1]) == 0, "Unexpected closing handshake: %r" % buf
                self.closed = True
                break
            else:
                raise ValueError("Don't understand how to parse this type of message: %r" % buf)
        self._buffer = buf
        return msgs

    def send(self, message):
        '''
        Send a message to the client. *message* should be convertable to a
        string; unicode objects should be encodable as utf-8.
        '''
        packed = self._pack_message(message)
        self.socket.sendall(packed)

    def _socket_recv(self):
        '''
        Gets new data from the socket and try to parse new messages.
        '''
        delta = self.socket.recv(self._socket_recv_bytes)
        if delta == '':
            return False
        self._buffer += delta
        msgs = self._parse_message_queue()
        self._message_queue.extend(msgs)
        return True

    def _socket_can_recv(self, timeout=0.0):
        '''
        Return ``True`` if new data can be read from the socket.
        '''
        r, w, e = [self.socket], [], []
        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error, err:
            if err.args[0] == EINTR:
                return False
            raise
        return self.socket in r

    def _get_new_messages(self):
        # read as long from socket as we need to get a new message.
        while self._socket_can_recv():
            self._socket_recv()
            if self._message_queue:
                return

    def count_messages(self):
        '''
        Returns the number of queued messages.
        '''
        self._get_new_messages()
        return len(self._message_queue)

    def has_messages(self):
        '''
        Returns ``True`` if new messages from the socket are available, else
        ``False``.
        '''
        if self._message_queue:
            return True
        self._get_new_messages()
        if self._message_queue:
            return True
        return False

    def read(self, fallback=None):
        '''
        Return new message or ``fallback`` if no message is available.
        '''
        if self.has_messages():
            return self._message_queue.popleft()
        return fallback

    def wait(self):
        '''
        Waits for and deserializes messages. Returns a single message; the
        oldest not yet processed.
        '''
        while not self._message_queue:
            # Websocket might be closed already.
            if self.closed:
                return None
            # no parsed messages, must mean buf needs more data
            new_data = self._socket_recv()
            if not new_data:
                return None
        return self._message_queue.popleft()

    def __iter__(self):
        '''
        Use ``WebSocket`` as iterator. Iteration only stops when the websocket
        gets closed by the client.
        '''
        while True:
            message = self.wait()
            if message is None:
                return
            yield message

    def _send_closing_frame(self, ignore_send_errors=False):
        '''
        Sends the closing frame to the client, if required.
        '''
        if self.version == 76 and not self.closed:
            try:
                self.socket.sendall("\xff\x00")
            except SocketError:
                # Sometimes, like when the remote side cuts off the connection,
                # we don't care about this.
                if not ignore_send_errors:
                    raise
            self.closed = True

    def close(self):
        '''
        Forcibly close the websocket.
        '''
        self._send_closing_frame()
