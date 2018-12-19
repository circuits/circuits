"""STOMP Protocol

This package contains a component implementing the STOMP Client protocol.
This can be used with products such as ActiveMQ, RabbitMQ, etc
"""
from .client import StompClient

__all__ = ('StompClient',)
# pylama:skip=1
