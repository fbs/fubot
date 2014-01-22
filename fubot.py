#!/usr/bin/env python

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from twisted.python import log

import sys

class FuProtocol(irc.IRCClient):
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

    def __init__(self, reactor, bot):
        self.reactor = reactor
        self.bot = bot

    def connect(self):
        self.reactor.connectTCP("localhost", 6667, self)

class Fubot(object):
    def __init__(self, reactor):
        self.reactor = reactor

    def start(self):
        self.network = FuNetwork(self.reactor, self)
        self.network.connect()

def main():
    log.startLogging(sys.stdout)
    fubot = Fubot(reactor)
    reactor.callWhenRunning(fubot.start)
    reactor.run()

if __name__ == '__main__':
    main()
