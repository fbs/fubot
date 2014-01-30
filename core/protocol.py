from twisted.words.protocols import irc
from twisted.python import log

class FuProtocol(object, irc.IRCClient):
    """The FuProtocol"""
    nickname = 'fubot'

    lineRate = 1

    # CTCP
    versionName = 'fubot'
    versionNum = '0.1'
    versionEnv = 'loonix'
    sourceURL = '127.0.0.1'

    channels = None

    def __init__(self, reactor, bot, network):
        self.reactor = reactor
        self.bot = bot
        self.network = network

    def signedOn(self):
        channels = self.network.config.get('channels', ())

        if 'nickserv' in self.network.config:
            log.msg('Nickserv setting found')
            self.msg('nickserv', 'IDENTIFY %s' %
                     self.network.config['nickserv'].encode('ascii'))

        for chan in channels:
            self.join(chan['name'].encode('ascii'))

    def connectionMade(self):
        self.network.connection = self
        self.channels = []
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        log.msg('Lost connection to [%s]: %s' % (self.network.name, reason))
        self.network.connection = None
        self.channels = []
        irc.IRCClient.connectionLost(self, reason)

    def privmsg(self, user, channel, message):
        self.bot.handle_privmsg(self, user, channel, message)

    def joined(self, channel):
        self.channels.append(channel)
        log.msg('Joined channel ' + channel)

    def left(self, channel):
        self.channels.remove(channel)
        log.msg('Left channel ' + channel)

    def kickedFrom(self, channel, kicker, message):
        self.channels.remove(channel)
        log.msg('Kicked from channel %s by %s [%s]' %
                (channel, kicker, message))

    def msg(self, user, message, length=None):
        if len(message) > 400:
            message = message[0:400] + '... truncated'
        irc.IRCClient.msg(self, user, message, length)

    def quit(self, message=''):
        log.msg('Sending quit to [%s]' % self.network.name)
        self.sendLine('QUIT :%s' % message)
