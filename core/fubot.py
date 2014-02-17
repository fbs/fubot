from twisted.python import log

from core.factory import FuFactory
from core.pluginmanager import PluginManager
from core.interface import  IMsgHandler, IRawMsgHandler

def _split_user(user):
    """Split nick!name@host into [nick, name, host]"""
    user, _ = user.split("!")
    realname, host = _.split("@")
    return [user, realname, host]

class Fubot(object):
    """The Fubot"""
    quitting = False
    quitmsg = 'time to go'

    def __init__(self, reactor, conf_filename, conf_json):
        self.reactor = reactor
        self.connections = dict()
        self.config_filename = conf_filename
        self.config = conf_json
        self.plugins = PluginManager()
        self.cmdprefix = self.config.get('command-prefix', '@').encode('ascii')

    def _connect(self):
        """Connect to networks"""
        for nwconfig in self.config['networks']:
            network = FuFactory(self.reactor, self, nwconfig)
            self.connections[network.name] = network
            self.plugins.add_network(network.name)
            network.connect()
            log.msg('Connected to network [%s] as [%s]' %
                    (network.name, network.protocol.nickname))

    def add_channel(self, network, channel):
        self.plugins.add_channel(network, channel)

    def _sigint(self, signal, frame):
        """Sigint handler"""
        log.msg('Received SIGINT')
        self.stop('Oh my, received SIGINT :/')

    def start(self):
        """Load all plugins in the config file and connect to all
        networks in the config file """
        # Get plugins from config file and load them
        plugins = self.config.get('plugins', [])
        for plugin in plugins:
            self.plugins.enable_global(plugin.get('name', ''))

        # Connect to the networks
        self._connect()

    def stop(self, msg='time to go'):
        """Stop all plugins and disconnect from all networks"""
        if self.quitting:
            return

        self.quitting = True

        for name in self.connections:
            log.msg('Disconnecting from network [%s]' % name)
            connection = self.connections[name].connection
            if connection:
                connection.quit(msg)
        self.connections = {}

        self.plugins.stop()

        self.reactor.callLater(2, self.reactor.stop)

    quit = stop

    def help(self, proto, user, channel, args):
        """Help the user"""
        help = ''
        user = user[0]

        if args:
            command = args[0]
            plugins = self.plugins.filter(network=proto.network,
                                          channel=channel,
                                          interface=IMsgHandler,
                                          command=command)

            if plugins:
                help = '[%s] %s' % (command, plugins[0].help(command))
            else:
                help = 'Sorry, can\'t help you with that command...'

        else:
            plugins = self.plugins.filter(network=proto.network,
                                          channel=channel,
                                          interface=IMsgHandler)
            help = 'Commands: '
            for plugin in plugins:
                help += plugin.list_commands()[0] + ' '

        proto.msg(channel, '%s: %s' % (user, help))

    def info(self, proto, user, channel, args):
        """Give some bot info"""
        proto.msg(channel, 'Hi %s! Im fubot, another useless bot. See %s'
                  % (user[0], 'https://git hub.com/fbs/fubot') +
                  ' to find out more about the sad mess that I am')

    def admin(self, proto, user, channel, message):
        pass

    def handle_privmsg(self, proto, user, channel, message):
        """Handle private messages"""
        cmd = ''
        args = ''
        user = _split_user(user)
        internalcmd = {'info': self.info,
                       'help': self.help,
                       'admin': self.admin}

        # "  @command arg1 arg2" -> ['@command', 'arg1', 'arg2']
        # "  @ command arg1" -> ['@', 'arg1']
        msglst = [w for w in message.split(' ') if w]

        # Private messages dont have to start with the command prefix
        if channel == proto.nickname:
            # print 'channel is nick'
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

        rawplugins = self.plugins.filter(network=proto.network,
                                         channel=channel,
                                         interface=IRawMsgHandler)

        for plugin in rawplugins:
            plugin.handle(proto, user, channel, message)


        if cmd in internalcmd:
            internalcmd[cmd](proto, user, channel, args)
            return

        plugins = self.plugins.filter(network=proto.network,
                                      channel=channel,
                                      interface=IMsgHandler,
                                      command=cmd)
        for plugin in plugins:
            # log.msg("Plugin found: %s" % plugin.name)
            plugin.handle(proto, cmd, user, channel, args)
