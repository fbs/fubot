from twisted.internet import ssl
from twisted.internet.protocol import ReconnectingClientFactory as RCF
from core.protocol import FuProtocol

from twisted.python import log

class FuNetwork(RCF):
    """Custom factory"""
    protocol = FuProtocol

    connection = None

    def buildProtocol(self, addr):
        return self.protocol(self.reactor, self.bot, self)

    def __init__(self, reactor, bot, config):
        self.reactor = reactor
        self.bot = bot
        self.config = config

    def connect(self):
        """Connect to a network using the settings from the config file
        supplied during init"""
        if (self.config.get('ssl', 'False')) == 'True':
            self.reactor.connectSSL(self.address,
                                    self.port,
                                    self,
                                    ssl.ClientContextFactory())
        else:
            self.reactor.connectTCP(self.address,
                                    self.port,
                                    self)

    def clientConnectionLost(self, connector, unused_reason):
        """Handle a lost connection"""
        if self.bot.quitting:
            log.msg('Factory shutting down, quitting')
            return
        RCF.clientConnectionLost(self, connector, unused_reason)
        log.msg('Factory reconnecting')

    def clientConnectionFailed(self, connector, reason):
        """Handle a failed connection"""
        log.msg('Failed to connect to [%s]: %s' % (self.name, reason))
        RCF.clientConnectionFailed(connector, reason)

    @property
    def name(self):
        """Network name"""
        return self.config.get('name', None)

    @property
    def port(self):
        """Port number"""
        return int(self.config.get('port', 6667))

    @property
    def address(self):
        """Network address"""
        return self.config.get('address')
