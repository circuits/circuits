# Module:   commands
# Date:     11th August 2014
# Author:   James Mills <prologic@shortcircuit.net.au>


"""Internet Relay Chat Protocol commands"""


from .events import request
from .message import Message


def AWAY(message=None):
    return request(Message("AWAY", message))


def NICK(nickname, hopcount=None):
    return request(Message("NICK", nickname, hopcount))


def USER(user, host, server, name):
    return request(Message("USER", user, host, server, name))


def PASS(password):
    return request(Message("PASS", password))


def PONG(daemon1, daemon2=None):
    return request(Message("PONG", daemon1, daemon2))


def QUIT(message=None):
    return request(Message("QUIT", message))


def JOIN(channels, keys=None):
    return request(Message("JOIN", channels, keys))


def PART(channels):
    return request(Message("PART", channels))


def PRIVMSG(receivers, message):
    return request(Message("PRIVMSG", receivers, message))


def NOTICE(receivers, message):
    return request(Message("NOTICE", receivers, message))


def KICK(channel, user, comment=None):
    return request(Message("KICK", channel, user, comment))


def TOPIC(channel, topic=None):
    return request(Message("TOPIC", channel, topic))


def MODE(target, *args):
    return request(Message("MODE", target, *args))


def INVITE(nickname, channel):
    return request(Message("INVITE", nickname, channel))


def NAMES(channels=None):
    return request(Message("NAMES", channels))


def WHOIS(nickmasks, server=None):
    return request(Message(server, nickmasks))


def WHO(name=None, o=None):
    return request(Message("WHO", name, o))
