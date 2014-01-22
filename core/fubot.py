from twisted.internet import protocol, reactor, ssl
from twisted.python import log

from core.factory import FuNetwork
from core.pluginmanager import plugin_manager

class Fubot(object):
    def __init__(self, reactor, conf_filename, conf_json):
        self.reactor = reactor
        self.connections = dict()
        self.config_filename = conf_filename
        self.config = conf_json

    def start(self):
        for nwconfig in self.config['networks']:
            nw = FuNetwork(self.reactor, self, nwconfig)
            self.connections[nw.name] = nw
            nw.connect()

    def handle_privmsg(self, proto, user, channel, message):
        log.msg("handle_privmsg: %s %s %s" % (user, channel, message))
        plugins = plugin_manager.filter()
        for plugin in plugins:
            plugin.handle(proto, user, channel, message)
