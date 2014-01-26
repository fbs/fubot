#!/usr/bin/env python

from twisted.python import log
from twisted.internet import reactor
from core.pluginmanager import plugin_manager
from core.fubot import Fubot

import json
import argparse
import signal

DEFAULT_SETTINGS = 'settings.json'

PARSER = argparse.ArgumentParser(prog='Fubot')

PARSER.add_argument('-c', '--config', dest='conffile',
                    help='The configuration file to use',
                    metavar='config_file',
                    action='store', default=DEFAULT_SETTINGS)

def main():
    """Load the config file and start everything"""
    args = PARSER.parse_args()
    conffile = args.conffile

    with open(conffile) as fdes:
        config = json.load(fdes)

    name = config.get('logfile', None)

    if name:
        if name == 'stdout':
            import sys
            log.startLogging(sys.stdout)
        else:
            log.startLogging(open(name, 'r'))

    fubot = Fubot(reactor, conffile, config)
    signal.signal(signal.SIGINT, fubot._sigint)
    reactor.callWhenRunning(fubot.start)
    reactor.addSystemEventTrigger('before','shutdown', plugin_manager.stop)
    reactor.run()

if __name__ == '__main__':
    main()
