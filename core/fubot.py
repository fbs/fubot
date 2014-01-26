from twisted.internet import reactor
from twisted.python import log
from twisted.words.protocols import irc

from core.factory import FuNetwork
from core.pluginmanager import plugin_manager
from core.interface import *

def _split_user(user):
    """Split nick!name@host into [nick, name, host]"""
    u, _ = user.split("!")
    r, h = _.split("@")
    return [u, r, h]

class Fubot(object):

    quitting = False
    quitmsg = 'time to go'

    def __init__(self, reactor, conf_filename, conf_json):
        self.reactor = reactor
        self.connections = dict()
        self.config_filename = conf_filename
        self.config = conf_json
        self.cmdprefix = self.config.get('command-prefix', '@').encode('ascii')

    def _connect(self):
        """Connect to networks"""
        for nwconfig in self.config['networks']:
            nw = FuNetwork(self.reactor, self, nwconfig)
            self.connections[nw.name] = nw
            nw.connect()
            log.msg('Connected to network [%s] as [%s]' %
                    (nw.name, nw.protocol.nickname))

    def _sigint(self, signal, frame):
        self.stop('Oh my, received SIGINT :/')

    def start(self):
        """Load all plugins in the config file and connect to all
        networks in the config file """
        # Get plugins from config file and load them
        plugins = self.config.get('plugins', [])
        for p in plugins:
            plugin_manager.load(p.get('name', ''))

        # Find all plugins that need to be initialized
        plugins = plugin_manager.filter(interface = IInitialize)
        plugin_data = self.config.get('plugin-data', '')
        for plugin in plugins:
            data = plugin_data.get(plugin.name, '')
            # log.msg('plugin data: %s' % data)
            plugin.initialize(data)

        # Connect to the networks
        self._connect()

    def stop(self, msg='time to go'):
        """Stop all plugins and disconnect from all networks"""
        self.quitting = True

        for name in self.connections:
            log.msg('Disconnecting from network [%s]' % name)
            connection = self.connections[name].connection
            connection.quit(msg)
        self.networks = {}

        plugin_manager.stop()

        self.reactor.callLater(5, self.reactor.stop)

    quit = stop

    def handle_privmsg(self, proto, user, channel, message):
        """Handle private messages"""
        cmd = ''
        args = ''
        user = _split_user(user)

        plugins = plugin_manager.filter(interface=IRawMsgHandler)
        for plugin in plugins:
            plugin.handle(proto, user, channel, message)

        # "  @command arg1 arg2" -> ['@command', 'arg1', 'arg2']
        # "  @ command arg1" -> ['@', 'arg1']
        msglst = [w for w in message.split(' ') if w]

        # Private messages dont have to start with the command prefix
        if channel == proto.nickname:
            channel = user[0]
            if msglst[0][0] == self.cmdprefix:
                cmd = msglst[0][1:]
            else:
                cmd = msglst[0]
            args = msglst[1:]

        # Channel messages do
        elif msglst[0][0] == self.cmdprefix:
            cmd = msglst[0][1:]
            args = msglst[1:]

        # Skip invalid commands
        else:
            return

        # log.msg("Command: %s" % cmd)
        plugins = plugin_manager.filter(interface=IMsgHandler, command=cmd)
        for plugin in plugins:
            # log.msg("Plugin found: %s" % plugin.name)
            plugin.handle(proto, user, channel, args)
