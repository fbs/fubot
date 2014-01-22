from twisted.internet import protocol, reactor, ssl

from core.protocol import FuProtocol

class FuNetwork(protocol.ReconnectingClientFactory):
    protocol = FuProtocol

    def buildProtocol(self, addr):
        proto = self.protocol(self.reactor, self.bot, self)
        return proto

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

    ## Network name
    @property
    def name(self):
        return self.config.get('name', 'fubot')
