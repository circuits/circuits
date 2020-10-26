# -*- coding: utf-8 -*-
""" Circuits component for handling Stomp Connection """

import logging
import ssl
import time
import traceback

from circuits import BaseComponent, Timer
from circuits.core.handlers import handler
from circuits.protocols.stomp.events import (
    client_heartbeat, connected, connection_failed, disconnected,
    heartbeat_timeout, message, on_stomp_error, server_heartbeat,
)
from circuits.protocols.stomp.transport import EnhancedStompFrameTransport

try:
    from stompest.config import StompConfig
    from stompest.protocol import StompSpec, StompSession
    from stompest.sync import Stomp
    from stompest.error import StompConnectionError, StompError
    from stompest.sync.client import LOG_CATEGORY
except ImportError:
    raise ImportError("No stomp support available.  Is stompest installed?")


StompSpec.DEFAULT_VERSION = '1.2'
ACK_CLIENT_INDIVIDUAL = StompSpec.ACK_CLIENT_INDIVIDUAL
ACK_AUTO = StompSpec.ACK_AUTO
ACK_CLIENT = StompSpec.ACK_CLIENT
ACK_MODES = (ACK_CLIENT_INDIVIDUAL, ACK_AUTO, ACK_CLIENT)

LOG = logging.getLogger(__name__)


class StompClient(BaseComponent):
    """ Send and Receive messages from a STOMP queue """
    channel = "stomp"

    def init(self, host, port, username=None, password=None,
             connect_timeout=3, connected_timeout=3,
             version=StompSpec.VERSION_1_2, accept_versions=["1.0", "1.1", "1.2"],
             heartbeats=(0, 0), ssl_context=None,
             use_ssl=True,
             key_file=None,
             cert_file=None,
             ca_certs=None,
             ssl_version=ssl.PROTOCOL_SSLv23,
             key_file_password=None,
             proxy_host=None,
             proxy_port=None,
             proxy_user=None,
             proxy_password=None,
             channel=channel):
        """ Initialize StompClient.  Called after __init__ """
        self.channel = channel
        if proxy_host:
            LOG.info("Connect to %s:%s through proxy %s:%d", host, port, proxy_host, proxy_port)
        else:
            LOG.info("Connect to %s:%s", host, port)

        if use_ssl and not ssl_context:

            ssl_params = dict(key_file=key_file,
                              cert_file=cert_file,
                              ca_certs=ca_certs,
                              ssl_version=ssl_version,
                              password=key_file_password)
            LOG.info("Request to use old-style socket wrapper: %s", ssl_params)
            ssl_context = ssl_params

        if use_ssl:
            uri = "ssl://%s:%s" % (host, port)
        else:
            uri = "tcp://%s:%s" % (host, port)

        # Configure failover options so it only tries to connect once
        self._stomp_server = "failover:(%s)?maxReconnectAttempts=1,startupMaxReconnectAttempts=1" % uri

        self._stomp_config = StompConfig(uri=self._stomp_server, sslContext=ssl_context,
                                         version=version,
                                         login=username,
                                         passcode=password)

        self._heartbeats = heartbeats
        self._accept_versions = accept_versions
        self._connect_timeout = connect_timeout
        self._connected_timeout = connected_timeout
        Stomp._transportFactory = EnhancedStompFrameTransport
        Stomp._transportFactory.proxy_host = proxy_host
        Stomp._transportFactory.proxy_port = proxy_port
        Stomp._transportFactory.proxy_user = proxy_user
        Stomp._transportFactory.proxy_password = proxy_password
        self._client = Stomp(self._stomp_config)
        self._subscribed = {}
        self.server_heartbeat = None
        self.client_heartbeat = None
        self.ALLOWANCE = 2  # multiplier for heartbeat timeouts

    @property
    def connected(self):
        if self._client.session:
            return self._client.session.state == StompSession.CONNECTED
        else:
            return False

    @property
    def subscribed(self):
        return self._subscribed.keys()

    @property
    def stomp_logger(self):
        return LOG_CATEGORY

    @handler("disconnect")
    def _disconnect(self, receipt=None):
        if self.connected:
            self._client.disconnect(receipt=receipt)
        self._client.close(flush=True)
        self.fire(disconnected(reconnect=False))
        self._subscribed = {}
        return "disconnected"

    def start_heartbeats(self):
        LOG.info("Client HB: %s  Server HB: %s", self._client.clientHeartBeat, self._client.serverHeartBeat)
        if self._client.clientHeartBeat:
            if self.client_heartbeat:
                # Timer already exists, just reset it
                self.client_heartbeat.reset()
            else:
                LOG.info("Client will send heartbeats to server")
                # Send heartbeats at 80% of agreed rate
                self.client_heartbeat = Timer((self._client.clientHeartBeat / 1000.0) * 0.8,
                                              client_heartbeat(), persist=True)
                self.client_heartbeat.register(self)
        else:
            LOG.info("No Client heartbeats will be sent")

        if self._client.serverHeartBeat:
            if self.server_heartbeat:
                # Timer already exists, just reset it
                self.server_heartbeat.reset()
            else:
                LOG.info("Requested heartbeats from server.")
                # Allow a grace period on server heartbeats
                self.server_heartbeat = Timer((self._client.serverHeartBeat / 1000.0) * self.ALLOWANCE,
                                              server_heartbeat(), persist=True)
                self.server_heartbeat.register(self)
        else:
            LOG.info("Expecting no heartbeats from Server")

    @handler("connect")
    def connect(self, event, host=None, *args, **kwargs):
        """ connect to Stomp server """
        LOG.info("Connect to Stomp...")
        try:
            self._client.connect(heartBeats=self._heartbeats,
                                 host=host,
                                 versions=self._accept_versions,
                                 connectTimeout=self._connect_timeout,
                                 connectedTimeout=self._connected_timeout)
            LOG.info("State after Connection Attempt: %s", self._client.session.state)
            if self.connected:
                LOG.info("Connected to %s", self._stomp_server)
                self.fire(connected())
                self.start_heartbeats()
                return "success"

        except StompConnectionError:
            LOG.debug(traceback.format_exc())
            self.fire(connection_failed(self._stomp_server))
            event.success = False
        return "fail"

    @handler("server_heartbeat")
    def check_server_heartbeat(self, event):
        """ Confirm that heartbeat from server hasn't timed out """
        now = time.time()
        last = self._client.lastReceived or 0
        if last:
            elapsed = now - last
        else:
            elapsed = -1
        LOG.debug("Last received data %d seconds ago", elapsed)
        if ((self._client.serverHeartBeat / 1000.0) * self.ALLOWANCE + last) < now:
            LOG.error("Server heartbeat timeout. %d seconds since last heartbeat.  Disconnecting.", elapsed)
            event.success = False
            self.fire(heartbeat_timeout())
            if self.connected:
                self._client.disconnect()
            # TODO: Try to auto-reconnect?

    @handler("client_heartbeat")
    def send_heartbeat(self, event):
        if self.connected:
            LOG.debug("Sending heartbeat")
            try:
                self._client.beat()
            except StompConnectionError:
                event.success = False
                self.fire(disconnected())

    @handler("generate_events")
    def generate_events(self, event):
        if not self.connected:
            return
        try:
            if self._client.canRead(1):
                frame = self._client.receiveFrame()
                LOG.debug("Recieved frame %s", frame)
                self.fire(message(frame))
        except StompConnectionError:
            self.fire(disconnected())

    @handler("send")
    def send(self, event, destination, body, headers=None, receipt=None):
        LOG.debug("send()")
        if not self.connected:
            LOG.error("Can't send when Stomp is disconnected")
            self.fire(on_stomp_error(None, Exception("Message send attempted with stomp disconnected")))
            event.success = False
            return
        try:
            self._client.send(destination, body=body.encode('utf-8'), headers=headers, receipt=receipt)
            LOG.debug("Message sent")
        except StompConnectionError:
            event.success = False
            self.fire(disconnected())
        except StompError as err:
            LOG.error("Error sending ack")
            event.success = False
            self.fire(on_stomp_error(None, err))

    @handler("subscribe")
    def _subscribe(self, event, destination, ack=ACK_CLIENT_INDIVIDUAL):
        if ack not in ACK_MODES:
            raise ValueError("Invalid client ack mode specified")
        LOG.info("Subscribe to message destination %s", destination)
        try:
            # Set ID to match destination name for easy reference later
            frame, token = self._client.subscribe(destination,
                                                  headers={StompSpec.ACK_HEADER: ack,
                                                           'id': destination})
            self._subscribed[destination] = token
        except StompConnectionError:
            event.success = False
            self.fire(disconnected())
        except StompError as err:
            event.success = False
            LOG.debug(traceback.format_exc())
            self.fire(on_stomp_error(None, err))

    @handler("unsubscribe")
    def _unsubscribe(self, event, destination):
        if destination not in self._subscribed:
            LOG.error("Unsubscribe Request Ignored. Not subscribed to %s", destination)
            return
        try:
            token = self._subscribed.pop(destination)
            frame = self._client.unsubscribe(token)
            LOG.debug("Unsubscribed: %s", frame)
        except StompConnectionError:
            event.success = False
            self.fire(disconnected())
        except StompError as err:
            LOG.error("Error sending ack")
            event.success = False
            self.fire(on_stomp_error(frame, err))

    @handler("message")
    def on_message(self, event, headers, message):
        LOG.info("Stomp message received")

    @handler("ack")
    def ack_frame(self, event, frame):
        LOG.debug("ack_frame()")
        try:
            self._client.ack(frame)
            LOG.debug("Ack Sent")
        except StompConnectionError:
            LOG.error("Error sending ack")
            event.success = False
            self.fire(disconnected())
        except StompError as err:
            LOG.error("Error sending ack")
            event.success = False
            self.fire(on_stomp_error(frame, err))

    def get_subscription(self, frame):
        """ Get subscription from frame """
        LOG.info(self._subscribed)
        _, token = self._client.message(frame)
        return self._subscribed[token]
