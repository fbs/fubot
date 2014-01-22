#!/usr/bin/env python

from twisted.python import log
from twisted.internet import reactor

from core.factory import FuNetwork
from core.protocol import FuProtocol
from core.fubot import Fubot

import json

def main():
    SETTINGS = 'settings.json'

    with open(SETTINGS) as fd:
        config = json.load(fd)

    name = config.get('logfile', None)

    if name:
        if name == 'stdout':
            import sys
            log.startLogging(sys.stdout)
        else:
            log.startLogging(open(name, 'r'))

    fubot = Fubot(reactor, SETTINGS, config)
    reactor.callWhenRunning(fubot.start)
    reactor.run()

if __name__ == '__main__':
    main()
