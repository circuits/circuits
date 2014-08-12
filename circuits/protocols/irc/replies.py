# Module:   replies
# Date:     11th August 2014
# Author:   James Mills <prologic@shortcircuit.net.au>


"""Internet Relay Chat Protocol replies"""


from operator import attrgetter


from .message import Message


def _M(*args, **kwargs):
    kwargs["add_nick"] = True
    return Message(*args, **kwargs)


def RPL_WELCOME(network):
    return _M("001", "Welcome to the {0:s} IRC Network".format(network))


def RPL_YOURHOST(host, version):
    return _M("002", "Your host is {0:s} running {1:s}".format(host, version))


def ERR_NOMOTD():
    return _M("422", "MOTD file is missing")


def ERR_NOSUCHNICK(nick):
    return _M("401", nick, "No such nick")


def ERR_NOSUCHCHANNEL(channel):
    return _M("403", channel, "No such channel")


def RPL_WHOREPLY(user, mask, server):
    # H = Here
    # G = Away
    # * = IRCOp
    # @ = Channel Op
    # + = Voiced

    return _M(
        "352", mask,
        user.userinfo.user, user.userinfo.host,
        server, user.nick,
        "G" if user.away else "H",
        "0 " + user.userinfo.name
    )


def RPL_ENDOFWHO(mask):
    return _M("315", mask, "End of WHO list")


def RPL_NOTOPIC(channel):
    return _M("331", channel, "No topic is set")


def RPL_NAMEREPLY(channel):
    prefix = "="
    nicks = " ".join(map(attrgetter("nick"), channel.users))
    return _M("353", prefix, channel.name, nicks)


def RPL_ENDOFNAMES():
    return _M("366", "End of NAMES list")


def ERR_UNKNOWNCOMMAND(command):
    return _M("421", command, "Unknown command")


def ERR_NICKNAMEINUSE(nick):
    return _M("433", nick, "Nickname is already in use")
