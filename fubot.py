#!/usr/bin/env python

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from twisted.python import log

import sys
import json

class FuProtocol(object, irc.IRCClient):
    nickname = 'fubot'

    lineRate = 0.3

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
        self.join('#test')

    def joined(self, channel):
        self.msg(channel, 'hello world')

    def connectionLost(self, reason):
        pass

    def privmsg(self, user, channel, message):
        pass

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
        log.msg("Connection to networks")

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

class Fubot(object):
    def __init__(self, reactor, conf_filename):
        self.reactor = reactor
        self.connections = dict()
        self.conf_filename = conf_filename
        with open(conf_filename) as fd:
            self.config = json.load(fd)
        if self.config['logfile'] == 'stdin':
            log.startLogging(sys.stdout)
        else:
            log.startLogging(open(self.config['logfile'],'a'))

    def start(self):
        for nwconfig in self.config['networks']:
            nw = FuNetwork(self.reactor, self, nwconfig)
            self.connections[nw.name] = nw
            nw.connect()

def main():
    SETTINGS = 'settings.json'
    fubot = Fubot(reactor, SETTINGS)
    reactor.callWhenRunning(fubot.start)
    reactor.run()

if __name__ == '__main__':
    main()
