from twisted.internet import protocol, reactor, ssl

from core.factory import FuNetwork

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
