"""Internet Relay Chat Protocol replies"""


from circuits.six import u

from .message import Message


def _M(*args, **kwargs):
    kwargs["add_nick"] = True
    return Message(*args, **kwargs)


def ERROR(host, reason=None):
    return Message(u("ERROR"), u(":Closing link: {0} ({1})".format(host, reason or u(""))))


def JOIN(name, prefix=None):
    return Message(u("JOIN"), name, prefix=prefix)


def KICK(channel, nick, reason=None, prefix=None):
    return Message(u("KICK"), channel, nick, reason, prefix=prefix)


def MODE(target, modes, params=None, prefix=None):
    if params is None:
        return Message(u("MODE"), target, modes, prefix=prefix)
    return Message(u("MODE"), target, modes, u(" ").join(params), prefix=prefix)


def PART(channel, nick, reason=None, prefix=None):
    return Message(u("PART"), channel, nick, reason, prefix=prefix)


def PING(server):
    return Message(u("PING"), u(":{0}").format(server))


def PONG(server, text):
    return Message(u("PONG"), server, u(":{0}").format(text))


def TOPIC(channel, topic, prefix=None):
    return Message(u("TOPIC"), channel, topic, prefix=prefix)


def RPL_WELCOME(network):
    return _M(u("001"), u("Welcome to the {0} IRC Network").format(network))


def RPL_YOURHOST(host, version):
    return _M(u("002"), u("Your host is {0} running {1}").format(host, version))


def RPL_CREATED(date):
    return _M(u("003"), u("This server was created {0}").format(date))


def RPL_MYINFO(server, version, umodes, chmodes):
    return _M(u("004"), server, version, umodes, chmodes)


def RPL_ISUPPORT(features):
    return _M(u("005"), *(features + (u("are supported by this server"),)))


def RPL_UMODEIS(modes):
    return _M(u("221"), modes)


def RPL_LUSERCLIENT(nusers, nservices, nservers):
    return _M(
        u("251"),
        u("There are {0} users and {1} services on {2} servers").format(
            nusers, nservices, nservers
        )
    )


def RPL_LUSEROP(noperators):
    return _M(u("252"), u("{0}").format(noperators), u("operator(s) online"))


def RPL_LUSERUNKOWN(nunknown):
    return _M(u("253"), u("{0}").format(nunknown), u("unknown connection(s)"))


def RPL_LUSERCHANNELS(nchannels):
    return _M(u("254"), u("{0}").format(nchannels), u("channels formed"))


def RPL_LUSERME(nclients, nservers):
    return _M(u("255"), u("I have {0} clients and {1} servers".format(nclients, nservers)))


def RPL_AWAY(nick, message):
    return _M(u("301"), nick, u(":{0}").format(message))


def RPL_UNAWAY():
    return _M(u("305"), u("You are no longer marked as being away"))


def RPL_NOWAWAY():
    return _M(u("306"), u("You have been marked as being away"))


def RPL_WHOISUSER(nick, user, host, realname):
    return _M(u("311"), nick, user, host, u("*"), u(":{0}").format(realname))


def RPL_WHOISSERVER(nick, server, server_info):
    return _M(u("312"), nick, server, server_info)


def RPL_WHOISOPERATOR(nick):
    return _M(u("313"), nick, u("is an IRC operator"))


def RPL_ENDOFWHO(mask):
    return _M(u("315"), mask, u("End of WHO list"))


def RPL_WHOISIDLE(nick, idle, signon):
    return _M(
        u("317"), nick,
        u("{0}").format(idle), u("{0}").format(signon),
        u("seconds idle, signon time")
    )


def RPL_ENDOFWHOIS(nick):
    return _M(u("318"), nick, u("End of WHOIS list"))


def RPL_WHOISCHANNELS(nick, channels):
    return _M(u("319"), nick, u(":{0}".format(u(" ").join(channels))))


def RPL_LISTSTART(header=None):
    return _M(u("321"), header or u("Channels :Users Name"))


def RPL_LIST(channel, nvisible, topic):
    return _M(u("322"), channel, u("{0}").format(nvisible), topic)


def RPL_LISTEND():
    return _M(u("323"), u("End of LIST"))


def RPL_CHANNELMODEIS(channel, mode, params=None):
    if params is None:
        return _M(u("324"), channel, mode)
    return _M(u("324"), channel, mode, params)


def RPL_NOTOPIC(channel):
    return _M(u("331"), channel, u("No topic is set"))


def RPL_TOPIC(channel, topic):
    return _M(u("332"), channel, topic)


def RPL_TOPICWHO(channel, setter, timestamp):
    return _M(u("333"), channel, setter, u("{0}".format(timestamp)))


def RPL_INVITING(channel, nick):
    return _M(u("341"), u("{0} {1}").format(channel, nick))


def RPL_SUMMONING(user):
    return _M(u("342"), u("{0} :Summoning user to IRC").format(user))


def RPL_INVITELIST(channel, invitemask):
    return _M(u("346"), u("{0} {1}").format(channel, invitemask))


def RPL_ENDOFINVITELIST(channel):
    return _M(u("347"), u("{0} :End of channel invite list").format(channel))


def RPL_VERSION(name, version, hostname, url):
    return _M(u("351"), name, version, hostname, url)


def RPL_WHOREPLY(channel, user, host, server, nick, status, hops, name):
    return _M(
        u("352"), channel, user, host, server, nick, status, u(":{0} {1}").format(hops, name)
    )


def RPL_NAMEREPLY(channel, names):
    return _M(u("353"), u("="), channel, u(" ").join(names))


def RPL_ENDOFNAMES(channel):
    return _M(u("366"), channel, u("End of NAMES list"))


def RPL_MOTD(text):
    return _M(u("372"), u("- {0}").format(text))


def RPL_MOTDSTART(server):
    return _M(u("375"), u("- {0} Message of the day -").format(server))


def RPL_ENDOFMOTD():
    return _M(u("376"), u("End of MOTD command"))


def RPL_YOUREOPER():
    return _M(u("381"), u("You are now an IRC operator"))


def ERR_NOSUCHNICK(nick):
    return _M(u("401"), nick, u("No such nick"))


def ERR_NOSUCHCHANNEL(channel):
    return _M(u("403"), channel, u("No such channel"))


def ERR_CANNOTSENDTOCHAN(channel):
    return _M(u("404"), channel, u("Cannot send to channel"))


def ERR_TOOMANYCHANNELS(channel):
    return _M(u("405"), channel, u("You have joined too many channels"))


def ERR_UNKNOWNCOMMAND(command):
    return _M(u("421"), command, u("Unknown command"))


def ERR_NOMOTD():
    return _M(u("422"), u("MOTD file is missing"))


def ERR_NONICKNAMEGIVEN():
    return _M(u("431"), u("No nickname given"))


def ERR_ERRONEUSNICKNAME(nick):
    return _M(u("432"), nick, u("Erroneous nickname"))


def ERR_NICKNAMEINUSE(nick):
    return _M(u("433"), nick, u("Nickname is already in use"))


def ERR_USERNOTINCHANNEL(nick, channel):
    return _M(u("441"), nick, channel, u("They aren't on that channel"))


def ERR_NOTREGISTERED():
    return _M(u("451"), "You have not registered")


def ERR_NEEDMOREPARAMS(command):
    return _M(u("461"), command, u("Need more parameters"))


def ERR_PASSWDMISMATCH():
    return _M(u("464"), u("Password incorrect"))


def ERR_UNKNOWNMODE(mode, channel=None):
    if channel is None:
        return _M(u("472"), mode, u("is unknown mode char to me"))
    return _M(u("472"), mode, u("is unknown mode char to me for channel {1}").format(channel))


def ERR_CHANOPRIVSNEEDED(channel):
    return _M(u("482"), channel, u("You're not channel operator"))


def ERR_NOPRIVILEGES():
    return _M(u("481"), u("Permission Denied- You're not an IRC operator"))


def ERR_NOOPERHOST():
    return _M(u("491"), u("No O-lines for your host"))


def ERR_USERSDONTMATCH():
    return _M(u("502"), u("Cannot change mode for other users"))
