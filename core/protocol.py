from twisted.words.protocols import irc
from twisted.python import log

class FuProtocol(object, irc.IRCClient):
    nickname = 'fubot'

    lineRate = 1

    # CTCP
    versionName = 'fubot'
    versionNum = '0.1'
    versionEnv = 'loonix'
    sourceURL = '127.0.0.1'

    def __init__(self, reactor, bot, network):
        self.reactor = reactor
        self.bot = bot
        self.network = network

    def signedOn(self):
        channels = self.network.config.get('channels', ())

        if 'nickserv' in self.network.config:
            log.msg('Nickserv setting found')
            self.msg('nickserv', 'IDENTIFY %s' % self.network.config['nickserv'].encode('ascii'))

        for chan in channels:
            self.join(chan['name'].encode('ascii'))

    # def joined(self, channel):
    #     self.msg(channel, 'hello world')

    def connectionLost(self, reason):
        pass

    def privmsg(self, user, channel, message):
        self.bot.handle_privmsg(self, user, channel, message)

    def msg(self, user, message, length=None):
        if len(message) > 400:
            message = message[0:400] + '... truncated'
        irc.IRCClient.msg(self, user, message, length)
