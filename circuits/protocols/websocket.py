"""

.. codeauthor: mnl
"""
import os
import random

from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
from circuits.net.events import close, read, write
from circuits.six import string_types


class WebSocketCodec(BaseComponent):

    """WebSocket Protocol

    Implements the Data Framing protocol for WebSocket.

    This component is used in conjunction with a parent component that
    receives Read events on its channel. When created (after a successful
    WebSocket setup handshake), the codec registers
    a handler on the parent's channel that filters out these Read
    events for a given socket (if used in a server) or all Read events
    (if used in a client). The data is decoded and the contained payload
    is emitted as Read events on the codec's channel.

    The data from write events sent to the codec's channel
    (with socket argument if used in a server) is
    encoded according to the WebSocket Data Framing protocol. The
    encoded data is then forwarded as write events on the parents channel.
    """

    channel = "ws"

    def __init__(self, sock=None, data=bytearray(), *args, **kwargs):
        """
        Creates a new codec.

        :param sock: the socket used in Read and write events
            (if used in a server, else None)
        """
        super(WebSocketCodec, self).__init__(*args, **kwargs)

        self._sock = sock

        self._pending_payload = bytearray()
        self._pending_type = None
        self._close_received = False
        self._close_sent = False
        self._buffer = bytearray()

        messages = self._parse_messages(bytearray(data))
        for message in messages:
            if self._sock is not None:
                self.fire(read(self._sock, message))
            else:
                self.fire(read(message))

    @handler("registered")
    def _on_registered(self, component, parent):
        if component is self:
            @handler("read", priority=10, channel=parent.channel)
            def _on_read_raw(self, event, *args):
                if self._sock is not None:
                    if args[0] != self._sock:
                        return
                    data = args[1]
                else:
                    data = args[0]
                messages = self._parse_messages(bytearray(data))
                for message in messages:
                    if self._sock is not None:
                        self.fire(read(self._sock, message))
                    else:
                        self.fire(read(message))
                event.stop()

            self.addHandler(_on_read_raw)

            @handler("disconnect", channel=parent.channel)
            def _on_disconnect(self, *args):
                if self._sock is not None:
                    if args[0] != self._sock:
                        return
                self.unregister()
            self.addHandler(_on_disconnect)

    def _parse_messages(self, data):
        msgs = []  # one chunk of bytes may result in several messages
        if self._close_received:
            return msgs
        data = self._buffer + data
        while data:
            # extract final flag, opcode and masking
            final = bool(data[0] & 0x80 != 0)
            opcode = data[0] & 0xf
            masking = bool(data[1] & 0x80 != 0)
            # evaluate payload length
            payload_length = data[1] & 0x7f
            offset = 2
            if payload_length >= 126:
                payload_bytes = 2 if payload_length == 126 else 8
                payload_length = 0
                for _ in range(payload_bytes):
                    payload_length = payload_length * 256 \
                        + data[offset]
                    offset += 1
            # retrieve optional masking key
            if masking:
                masking_key = data[offset:offset + 4]
                offset += 4
            # if not enough bytes available yet, retry after next read
            if len(data) - offset < payload_length:
                self._buffer = data
                break
            self._buffer = bytearray()
            # rest of _buffer is payload
            msg = data[offset:offset + payload_length]
            if masking:  # unmask
                msg = list(msg)
                for i, c in enumerate(msg):
                    msg[i] = c ^ masking_key[i % 4]
                msg = bytearray(msg)
            # remove bytes of processed frame from byte _buffer
            offset += payload_length
            data = data[offset:]
            # if there have been parts already, combine
            msg = self._pending_payload + msg
            if final:
                if opcode < 8:
                    # if text or continuation of text, convert
                    if opcode == 1 \
                            or opcode == 0 and self._pending_type == 1:
                        msg = msg.decode("utf-8", "replace")
                    self._pending_type = None
                    self._pending_payload = bytearray()
                    msgs.append(msg)
                # check for client closing the connection
                elif opcode == 8:
                    self._close_received = True
                    if self._sock:
                        self.fire(close(self._sock))
                    else:
                        self.fire(close())
                    break
                # check for Ping
                elif opcode == 9:
                    if self._close_sent:
                        return
                    frame = bytearray(b'\x8a')
                    frame += self._encode_tail(msg, self._sock is None)
                    self._write(frame)
            else:
                self._pending_payload = msg
                if opcode != 0:
                    self._pending_type = opcode
        return msgs

    @handler("write")
    def _on_write(self, *args):
        if self._close_sent:
            return

        if self._sock is not None:
            if args[0] != self._sock:
                return
            data = args[1]
        else:
            data = args[0]

        frame = bytearray()
        first = 0x80  # set FIN flag, we never fragment
        if isinstance(data, string_types):
            first += 1  # text
            data = bytearray(data, "utf-8")
        else:
            first += 2  # binary
        frame.append(first)
        frame += self._encode_tail(data, self._sock is None)
        self._write(frame)

    def _encode_tail(self, data, mask=False):
        tail = bytearray()
        data_length = len(data)
        if data_length <= 125:
            len_byte = data_length
            lbytes = 0
        elif data_length <= 0xffff:
            len_byte = 126
            lbytes = 2
        else:
            len_byte = 127
            lbytes = 8
        if mask:
            len_byte = len_byte | 0x80
        tail.append(len_byte)
        for i in range(lbytes - 1, -1, -1):
            tail.append(data_length >> (i * 8) & 0xff)
        if mask:
            try:
                masking_key = bytearray(list(os.urandom(4)))
            except NotImplementedError:
                masking_key \
                    = bytearray([random.randint(0, 255) for i in range(4)])
            tail += masking_key
            for i, c in enumerate(data):
                tail.append(c ^ masking_key[i % 4])
        else:
            tail += data
        return tail

    def _write(self, data):
        if self._sock is not None:
            self.fire(write(self._sock, data), self.parent.channel)
        else:
            self.fire(write(data), self.parent.channel)

    @handler("close")
    def _on_close(self, *args):
        if self._sock is not None:
            if args and (args[0] != self._sock):
                return
        if not self._close_sent:
            self._write(b"\x88\x00")
            self._close_sent = True
        if self._close_received and self._close_sent:
            if self._sock:
                self.fire(close(self._sock), self.parent.channel)
            else:
                self.fire(close(), self.parent.channel)
