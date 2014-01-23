from twisted.internet import protocol, reactor, ssl
from twisted.python import log

from core.factory import FuNetwork
from core.pluginmanager import plugin_manager
from core.interface import *

def _split_user(user):
    """Split nick!name@host into [nick, name, host]"""
    u, _ = user.split("!")
    r, h = _.split("@")
    return [u, r, h]

class Fubot(object):
    def __init__(self, reactor, conf_filename, conf_json):
        self.reactor = reactor
        self.connections = dict()
        self.config_filename = conf_filename
        self.config = conf_json
        self.cmdprefix = self.config.get('command-prefix', '@').encode('ascii')

    def start(self):
        # Get plugins from config file and load them
        plugins = self.config.get('plugins', [])
        plugin_manager.load(plugins)

        # Find all plugins that need to be initialized
        plugins = plugin_manager.filter(interface = IInitialize)
        plugin_data = self.config.get('plugin-data', '')
        for plugin in plugins:
            data = plugin_data[plugin.name]
            # log.msg('plugin data: %s' % data)
            plugin.initialize(data)

        # Connect to the networks
        self._connect()

    def _connect(self):
        for nwconfig in self.config['networks']:
            nw = FuNetwork(self.reactor, self, nwconfig)
            self.connections[nw.name] = nw
            nw.connect()

    def handle_privmsg(self, proto, user, channel, message):
        # log.msg("handle_privmsg: %s %s %s" % (user, channel, message))
        user = _split_user(user)

        plugins = plugin_manager.filter(interface=IRawMsgHandler)
        for plugin in plugins:
            plugin.handle(proto, user, channel, message)

        # "  @command arg1 arg2" -> ['@command', 'arg1', 'arg2']
        # "  @ command arg1" -> ['@', 'arg1']
        msglst = [w for w in message.split(' ') if w]

        if msglst[0][0] == self.cmdprefix:
            cmd = msglst[0][1:]
            args = msglst[1:]

            # Nothing after the @, so no command
            if not cmd:
                log.msg("Invalid command")
                return

            # log.msg("Command: %s" % cmd)
            plugins = plugin_manager.filter(interface=IMsgHandler, command=cmd)
            for plugin in plugins:
                # log.msg("Plugin found: %s" % plugin.name)
                plugin.handle(proto, user, channel, args)
