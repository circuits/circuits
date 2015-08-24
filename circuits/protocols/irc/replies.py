"""Internet Relay Chat Protocol replies"""


from .message import Message


def _M(*args, **kwargs):
    kwargs["add_nick"] = True
    return Message(*args, **kwargs)


def RPL_WELCOME(network):
    return _M(u"001", u"Welcome to the {0} IRC Network".format(network))


def RPL_YOURHOST(host, version):
    return _M(u"002", u"Your host is {0} running {1}".format(host, version))


def ERR_NOMOTD():
    return _M(u"422", u"MOTD file is missing")


def ERR_NOSUCHNICK(nick):
    return _M(u"401", nick, u"No such nick")


def ERR_NOSUCHCHANNEL(channel):
    return _M(u"403", channel, u"No such channel")


def RPL_WHOREPLY(user, mask, server):
    # H = Here
    # G = Away
    # * = IRCOp
    # @ = Channel Op
    # + = Voiced

    return _M(
        u"352", mask,
        user.userinfo.user, user.userinfo.host,
        server, user.nick,
        u"G" if user.away else u"H",
        u"0 " + user.userinfo.name
    )


def RPL_ENDOFWHO(mask):
    return _M(u"315", mask, u"End of WHO list")


def RPL_NOTOPIC(channel):
    return _M(u"331", channel, u"No topic is set")


def RPL_NAMEREPLY(channel, names):
    return _M(u"353", u"=", channel, u" ".join(names))


def RPL_ENDOFNAMES():
    return _M(u"366", u"End of NAMES list")


def ERR_UNKNOWNCOMMAND(command):
    return _M(u"421", command, u"Unknown command")


def ERR_NICKNAMEINUSE(nick):
    return _M(u"433", nick, u"Nickname is already in use")
