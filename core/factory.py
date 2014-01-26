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
        if (self.config.get('ssl', 'False')) == 'True':
            self.reactor.connectSSL(self.config['hostname'],
                                    int(self.config.get('port', 6697)),
                                    self,
                                    ssl.ClientContextFactory())
        else:
            self.reactor.connectTCP(self.config['hostname'],
                                    int(self.config.get('port', 6667)),
                                    self)

    def clientConnectionLost(self, connector, unused_reason):
        if self.bot.quitting:
            log.msg('Factory shutting down, quitting')
            return
        RCF.clientConnectionLost(self, connector, unused_reason)
        log.msg('Factory reconnecting')

    def clientConnectionFailed(self, connector, reason):
        log.msg('Failed to connect to [%s]: %s' % (self.name, reason))
        RCF.clientConnectionFailed(connector, reason)

    ## Network name
    @property
    def name(self):
        return self.config.get('name', 'fubot')
